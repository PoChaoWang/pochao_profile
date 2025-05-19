from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType,
    DateType,
)
from pyspark.sql.functions import from_json, col
from dotenv import load_dotenv
import os
import psycopg2
import logging
import os

load_dotenv()

LOG_DIR = "../logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=os.path.join(LOG_DIR, "spark.log"),
    filemode="a",
)

# --- Spark 和 PostgreSQL 配置 ---
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DATABASE = os.getenv("POSTGRES_DB", "highway_traffic")
POSTGRES_USER = os.getenv("POSTGRES_USER", "spark_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "spark_password")
POSTGRES_TARGET_TABLE = "highway_traffic_raw"
POSTGRES_TARGET_SCHEMA = "public"

POSTGRES_JDBC_URL = (
    f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
)
POSTGRES_DRIVER_CLASS = "org.postgresql.Driver"

_table_creation_attempted = False


def ensure_table_exists():
    """
    Check and create the target PostgreSQL table if necessary.
    This function should be called once after SparkSession initialization and before starting the stream.
    """
    global _table_creation_attempted
    if _table_creation_attempted:
        return

    conn = None
    try:
        logging.info(
            f"\n[INFO] Attempting to connect to PostgreSQL ({POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}) to check/create table..."
        )
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DATABASE,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT,
        )
        cursor = conn.cursor()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {POSTGRES_TARGET_SCHEMA}.{POSTGRES_TARGET_TABLE} (
            capture_date_utc DATE,
            capture_time_utc VARCHAR(30),
            object_id VARCHAR(255),
            uuid UUID PRIMARY KEY,
            class VARCHAR(100),
            bounding_box_x1 REAL,
            bounding_box_y1 REAL,
            bounding_box_x2 REAL,
            bounding_box_y2 REAL,
            confidence REAL,
            center_pixels_x REAL,
            center_pixels_y REAL,
            zone_name VARCHAR(255),
            speed_kmh REAL
        );
        """
        logging.info(
            f"Executing SQL: CREATE TABLE IF NOT EXISTS {POSTGRES_TARGET_SCHEMA}.{POSTGRES_TARGET_TABLE} ..."
        )
        cursor.execute(create_table_query)
        conn.commit()
        logging.info(
            f"[SUCCESS] Table {POSTGRES_TARGET_SCHEMA}.{POSTGRES_TARGET_TABLE} has been checked/created."
        )
    except psycopg2.OperationalError as e:
        logging.error(f"Unable to connect to PostgreSQL service: {e}")
        logging.error(
            f"[INFO] Please ensure that the PostgreSQL service is running at {POSTGRES_HOST}:{POSTGRES_PORT} and is reachable."
        )
        raise
    except (Exception, psycopg2.Error) as error:
        logging.error(
            f"[ERROR] Error occurred while connecting to PostgreSQL or creating the table: {error}"
        )
        raise
    finally:
        if conn:
            if "cursor" in locals() and cursor:
                cursor.close()
            conn.close()
            logging.info("PostgreSQL connection closed.")
    _table_creation_attempted = True


def spark_to_postgres():
    logging.info("\n Initializing SparkSession...")
    try:
        spark = (
            SparkSession.builder.appName("sparkToPostgres")
            .master("local[*]")
            .config(
                "spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.7.3",
            )
            .getOrCreate()
        )
        spark.sparkContext.setLogLevel("INFO")
        logging.info("SparkSession initialized。")
    except Exception as e:
        logging(f"SparkSession initialization failed: {e}")
        return

    try:
        ensure_table_exists()
    except Exception as e:
        logging.error(
            f"[FATAL] Unable to ensure the target table exists, terminating program: {e}"
        )
        spark.stop()
        return

    logging.info("\n Defining DataFrame(Schema)...")
    trafficSchema = StructType(
        [
            StructField("capture_date_utc", DateType(), True),
            StructField("capture_time_utc", StringType(), True),
            StructField("object_id", StringType(), True),
            StructField("uuid", StringType(), True),
            StructField("class", StringType(), True),
            StructField("bounding_box_x1", DoubleType(), True),
            StructField("bounding_box_y1", DoubleType(), True),
            StructField("bounding_box_x2", DoubleType(), True),
            StructField("bounding_box_y2", DoubleType(), True),
            StructField("confidence", DoubleType(), True),
            StructField("center_pixels_x", DoubleType(), True),
            StructField("center_pixels_y", DoubleType(), True),
            StructField("zone_name", StringType(), True),
            StructField("speed_kmh", DoubleType(), True),
        ]
    )

    kafka_topic = os.getenv("KAFKA_TOPIC", "yolo_detections_topic")
    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")

    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers)
        .option("subscribe", kafka_topic)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .load()
        .selectExpr("CAST(value AS STRING)")
        .select(from_json(col("value"), trafficSchema).alias("data"))
        .select("data.*")
    )

    logging.info(
        f"Starting to read streaming data from Kafka topic '{kafka_topic}' at '{kafka_bootstrap_servers}'..."
    )

    def write_to_postgres_batch(batch_df, batch_id):
        if batch_df.rdd.isEmpty():
            logging.info(f"Batch {batch_id}: DataFrame is empty, no data to write.")
            return

        logging.info(f"\n Batch {batch_id}: Preparing to write data to PostgreSQL...")
        logging.info(
            f"       Target Table: {POSTGRES_TARGET_SCHEMA}.{POSTGRES_TARGET_TABLE}"
        )
        try:
            (
                batch_df.write.format("jdbc")
                .mode("append")
                .option("url", POSTGRES_JDBC_URL)
                .option("dbtable", f"{POSTGRES_TARGET_SCHEMA}.{POSTGRES_TARGET_TABLE}")
                .option("user", POSTGRES_USER)
                .option("password", POSTGRES_PASSWORD)
                .option("driver", POSTGRES_DRIVER_CLASS)
                .option("stringtype", "unspecified")
                .save()
            )
            logging.info(
                f"[SUCCESS] Batch {batch_id}: Data successfully written to PostgreSQL."
            )
        except Exception as e:
            logging.error(f"Batch {batch_id}: Failed to write to PostgreSQL: {e}")

    query = (
        df.writeStream.foreachBatch(write_to_postgres_batch)
        .outputMode("append")
        .option("checkpointLocation", "/tmp/spark_checkpoints/postgres_highway_traffic")
        .start()
    )

    logging.info(
        "\n Streaming query started. Waiting for termination (e.g., manual stop)..."
    )
    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        logging.info("\n Manual interruption detected. Stopping streaming query...")
    finally:
        logging.info("\n Stopping SparkSession...")
        spark.stop()
        logging.info("[COMPLETE] Program execution finished.")


if __name__ == "__main__":
    spark_to_postgres()
