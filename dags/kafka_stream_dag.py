# Importing required modules
from datetime import datetime, date, timedelta
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
# from kafka_streaming_service import initiate_stream


# Configuration for the DAG's start date
DAG_START_DATE = datetime(2024, 2, 6, 23, 00)

# Default arguments for the DAG
DAG_DEFAULT_ARGS = {
    'owner': 'airflow',
    'start_date': DAG_START_DATE,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}

# Creating the DAG with its configuration
with DAG(
    'scrapper_dag',  # Renamed for uniqueness
    default_args=DAG_DEFAULT_ARGS,
    schedule_interval='14 19 * * 4',
    catchup=False,
    description='runs scrapper and streams to kafka topic',
    max_active_runs=1
) as dag:
    
    kafka_stream_task = DockerOperator(
        task_id='docker_stream_to_kafka_topic',
        image='ccalderon911217/shot_chart_scraper:latest',
        api_version='auto',
        auto_remove=True,
        docker_url="tcp://docker-proxy:2375",
        network_mode='docker_streaming',
        dag=dag
    )

    kafka_stream_task

