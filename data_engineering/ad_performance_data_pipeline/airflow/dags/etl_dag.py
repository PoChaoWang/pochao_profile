from datetime import datetime, timedelta
from airflow import DAG
from docker.types import Mount
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
import subprocess

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    }

def run_etl_script():
    script_path = "/opt/airflow/etl/etl_script.py"
    result = subprocess.run(["python", script_path], capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"etl script failed with error:\n{result.stderr}")
    else:
        print(result.stdout)

dag = DAG(
    'etl_and_dbt',
    default_args=default_args,
    description='Extract, Transform, Load (ETL) and Data Transformation Tool (DBT) pipeline',
    start_date=datetime(2024,12,31),
    schedule_interval='0 0 * * *',  # Run every day at midnight
    catchup=False,
    )

task1 = PythonOperator(
    task_id='run_etl_script',
    python_callable=run_etl_script,
    dag=dag,
)

task2 = DockerOperator(
    task_id='run_dbt',
    image='ghcr.io/dbt-labs/dbt-postgres:1.9.0',
    command=
      [
        "run",
        "--profiles-dir",
        "/root",
        "--project-dir",
        "/dbt",
        "--full-refresh"
      ],
      auto_remove=True,
      docker_url="unix://var/run/docker.sock",
      network_mode="bridge",
      mounts=[
        Mount(source='/Users/pochaowang/Documents/Profile/ad_performance_data_pipeline/custom_ad_data', target='/dbt', type='bind'),
        Mount(source='/Users/pochaowang/.dbt',target='/root',type='bind')
    ],  
    dag=dag
)

task1 >> task2