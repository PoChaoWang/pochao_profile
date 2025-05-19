from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    TimestampType,
    DoubleType,
)
from config import configuration
from pyspark.sql.functions import from_json, col


def main():
    spark = (
        SparkSession.builder.appName("taipei_taxi")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk:1.11.469",
        )
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config(
            "spark.hadoop.fs.s3a.access.key", configuration.get("AWS_ACCESS_KEY_ID")
        )
        .config("spark.hadoop.fs.s3a.secret.key", configuration.get("AWS_SECRET_KEY"))
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        )
        .getOrCreate()
    )

    # Adjust the log level to minimize the console output on executors
    spark.sparkContext.setLogLevel("WARN")

    # Vehicle schema
    vehicleSchema = StructType(
        [
            StructField("vehicle_id", StringType(), True),
            StructField("deviceId", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("latitude", DoubleType(), True),
            StructField("longitude", DoubleType(), True),
            StructField("speed", DoubleType(), True),
            StructField("direction", StringType(), True),
            StructField("make", StringType(), True),
            StructField("model", StringType(), True),
            StructField("year", IntegerType(), True),
            StructField("fuelType", StringType(), True),
            StructField("status", StringType(), True),
        ]
    )

    # GPS schema
    gpsSchema = StructType(
        [
            StructField("gps_id", StringType(), True),
            StructField("deviceId", StringType(), True),
            StructField("latitude", DoubleType(), True),
            StructField("longitude", DoubleType(), True),
            StructField("speed", DoubleType(), True),
            StructField("timestamp", TimestampType(), True),
        ]
    )

    # Traffic schema
    trafficSchema = StructType(
        [
            StructField("traffic_id", StringType(), True),
            StructField("deviceId", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("latitude", DoubleType(), True),
            StructField("longitude", DoubleType(), True),
            StructField("status", StringType(), True),
        ]
    )

    # Weather schema
    weatherSchema = StructType(
        [
            StructField("driver_id", StringType(), True),
            StructField("deviceId", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("latitude", DoubleType(), True),
            StructField("longitude", DoubleType(), True),
            StructField("temperature", DoubleType(), True),
            StructField("weatherCondition", StringType(), True),
            StructField("humidity", DoubleType(), True),
            StructField("windSpeed", DoubleType(), True),
            StructField("precipitation", DoubleType(), True),
            StructField("airQualityIndex", DoubleType(), True),
        ]
    )

    # Driver schema
    driverSchema = StructType(
        [
            StructField("driver_id", StringType(), True),
            StructField("deviceId", StringType(), True),
            StructField("phone_number", StringType(), True),
            StructField("name", StringType(), True),
            StructField("email", StringType(), True),
            StructField("rating", DoubleType(), True),
            StructField("total_trips", IntegerType(), True),
            StructField("years_experience", IntegerType(), True),
            StructField("license_number", StringType(), True),
            StructField("created_at", TimestampType(), True),
        ]
    )

    # User schema
    userSchema = StructType(
        [
            StructField("user_id", StringType(), True),
            StructField("phone_number", StringType(), True),
            StructField("name", StringType(), True),
            StructField("email", StringType(), True),
            StructField("rating", DoubleType(), True),
            StructField("total_trips", IntegerType(), True),
            StructField("created_at", TimestampType(), True),
        ]
    )

    # Payment schema
    paymentSchema = StructType(
        [
            StructField("payment_id", StringType(), True),
            StructField("trip_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("driver_id", StringType(), True),
            StructField("amount", DoubleType(), True),
            StructField("currency", StringType(), True),
            StructField("payment_method", StringType(), True),
            StructField("status", StringType(), True),
            StructField("base_fare", DoubleType(), True),
            StructField("distance_fare", DoubleType(), True),
            StructField("time_fare", DoubleType(), True),
            StructField("timestamp", TimestampType(), True),
        ]
    )

    def read_kafka_topic(topic, schema, add_watermark=True):
        df = (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", "broker:29092")
            .option("subscribe", topic)
            .option("startingOffsets", "earliest")
            .load()
            .selectExpr("CAST(value AS STRING)")
            .select(from_json(col("value"), schema).alias("data"))
            .select("data.*")
        )

        if add_watermark and "timestamp" in schema.fieldNames():
            df = df.withWatermark("timestamp", "2 minutes")

        return df

    def streamWriter(input: DataFrame, checkpointFolder, output):
        return (
            input.writeStream.format("parquet")
            .option("checkpointLocation", checkpointFolder)
            .option("path", output)
            .outputMode("append")
            .start()
        )

    # Create DataFrames for each topic
    vehicleDF = read_kafka_topic("vehicle_data", vehicleSchema).alias("vehicle")
    gpsDF = read_kafka_topic("gps_data", gpsSchema).alias("gps")
    trafficDF = read_kafka_topic("traffic_data", trafficSchema).alias("traffic")
    weatherDF = read_kafka_topic("weather_data", weatherSchema).alias("weather")
    paymentDF = read_kafka_topic("payment_data", paymentSchema).alias("payment")
    driverDF = read_kafka_topic("driver_data", driverSchema, add_watermark=False)
    userDF = read_kafka_topic("user_data", userSchema, add_watermark=False)

    # Write streams to S3
    query1 = streamWriter(
        vehicleDF,
        "s3a://tpe-taxi-spark-streaming-data/checkpoints/vehicle_data",
        "s3a://tpe-taxi-spark-streaming-data/data/vehicle_data",
    )
    query2 = streamWriter(
        gpsDF,
        "s3a://tpe-taxi-spark-streaming-data/checkpoints/gps_data",
        "s3a://tpe-taxi-spark-streaming-data/data/gps_data",
    )
    query3 = streamWriter(
        trafficDF,
        "s3a://tpe-taxi-spark-streaming-data/checkpoints/traffic_data",
        "s3a://tpe-taxi-spark-streaming-data/data/traffic_data",
    )
    query4 = streamWriter(
        weatherDF,
        "s3a://tpe-taxi-spark-streaming-data/checkpoints/weather_data",
        "s3a://tpe-taxi-spark-streaming-data/data/weather_data",
    )
    query5 = streamWriter(
        paymentDF,
        "s3a://tpe-taxi-spark-streaming-data/checkpoints/payment_data",
        "s3a://tpe-taxi-spark-streaming-data/data/payment_data",
    )
    query6 = streamWriter(
        userDF,
        "s3a://tpe-taxi-spark-streaming-data/checkpoints/user_data",
        "s3a://tpe-taxi-spark-streaming-data/data/user_data",
    )
    query7 = streamWriter(
        driverDF,
        "s3a://tpe-taxi-spark-streaming-data/checkpoints/driver_data",
        "s3a://tpe-taxi-spark-streaming-data/data/driver_data",
    )

    # Wait for all queries to terminate
    queries = [query1, query2, query3, query4, query5, query6, query7]
    for query in queries:
        try:
            query.awaitTermination()
        except Exception as e:
            print(f"Query failed with error: {str(e)}")
            # Stop all other queries when one fails
            for q in queries:
                try:
                    q.stop()
                except:
                    pass
            raise e  # Re-raise exception to ensure proper program termination


if __name__ == "__main__":
    main()
