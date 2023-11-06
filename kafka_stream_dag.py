# Importing required modules
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from kafka_streaming_service import initiate_stream  
# Configuration for the DAG's start date
DAG_START_DATE = datetime(2018, 12, 21, 12, 12)

# Default arguments for the DAG
DAG_DEFAULT_ARGS = {
    'owner': 'airflow',
    'start_date': DAG_START_DATE,
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

# Creating the DAG with its configuration
with DAG(
    'name_stream_dag',  # Renamed for uniqueness
    default_args=DAG_DEFAULT_ARGS,
    schedule_interval='0 1 * * *',
    catchup=False,
    description='Stream random names to Kafka topic',
    max_active_runs=1
) as dag:
    
    # Defining the data streaming task using PythonOperator
    kafka_stream_task = PythonOperator(
        task_id='stream_to_kafka_task', 
        python_callable=initiate_stream,
        dag=dag
    )

    kafka_stream_task

