from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import subprocess
import os

# Default arguments for the DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'data_platform_pipeline',
    default_args=default_args,
    description='A sample data pipeline for the data platform',
    schedule_interval=timedelta(days=1),
)

def run_ingestion():
    """Run the batch ingestion script."""
    # In a real scenario, we might use Airbyte or a Spark job
    print("Starting ingestion...")
    # Simulate ingestion by running a script
    # subprocess.run(["python3", "/opt/airflow/dags/scripts/ingest_batch.py"])
    return "Ingestion completed successfully"

def run_cleaning():
    """Run the cleaning script."""
    print("Starting data cleaning...")
    # Simulate cleaning by running a script
    # subprocess.run(["python3", "/opt/airflow/dags/scripts/clean_data.py"])
    return "Cleaning completed successfully"

def run_analytics():
    """Run the analytics step."""
    print("Starting analytics and reporting...")
    return "Analytics completed successfully"

# Define tasks
ingest_task = PythonOperator(
    task_id='ingest_data',
    python_callable=run_ingestion,
    dag=dag,
)

clean_task = PythonOperator(
    task_id='clean_data',
    python_callable=run_cleaning,
    dag=dag,
)

analytics_task = PythonOperator(
    task_id='generate_reports',
    python_callable=run_analytics,
    dag=dag,
)

# Set dependencies
ingest_task >> clean_task >> analytics_task
