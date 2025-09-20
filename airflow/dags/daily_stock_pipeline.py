"""
DAG cho việc crawl OHLCV data hàng ngày
Author: Banking Portfolio Team
Description: Daily OHLCV data pipeline với logging và error handling
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# Add project root to path
sys.path.insert(0, '/opt/airflow/finance_portfolio')

# Banking stocks list
BANKING_STOCKS = [
    'ACB', 'BID', 'CTG', 'EIB', 'HDB', 'LPB', 'MBB', 'MSB', 'NAB', 'NCB',
    'OCB', 'SHB', 'SSB', 'STB', 'TCB', 'TPB', 'VCB', 'VIB', 'VPB', 'BAB',
    'BVB', 'CBB', 'KLB', 'NVB', 'PGB', 'SEAB', 'ABB'
]

def crawl_ohlcv_data(**context):
    """Crawl OHLCV data cho tất cả banking stocks"""
    try:
        import subprocess
        from datetime import datetime
        
        # Get execution date (previous day)
        execution_date = context['ds']
        
        print(f"Starting OHLCV crawl for date: {execution_date}")
        
        # Run ingest_stock.py for all banking stocks
        script_path = '/opt/airflow/finance_portfolio/scripts/ingest_stock.py'
        
        success_count = 0
        failed_stocks = []
        
        for stock in BANKING_STOCKS:
            try:
                cmd = f"cd /opt/airflow/finance_portfolio && python {script_path} --symbol {stock} --date {execution_date}"
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=300  # 5 minutes timeout per stock
                )
                
                if result.returncode == 0:
                    success_count += 1
                    print(f"✅ Successfully crawled {stock}")
                else:
                    failed_stocks.append(stock)
                    print(f"❌ Failed to crawl {stock}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                failed_stocks.append(stock)
                print(f"⏰ Timeout while crawling {stock}")
            except Exception as e:
                failed_stocks.append(stock)
                print(f"💥 Error crawling {stock}: {str(e)}")
        
        # Summary
        total_stocks = len(BANKING_STOCKS)
        success_rate = (success_count / total_stocks) * 100
        
        print(f"\n📊 OHLCV Crawl Summary for {execution_date}:")
        print(f"✅ Successful: {success_count}/{total_stocks} ({success_rate:.1f}%)")
        print(f"❌ Failed: {len(failed_stocks)}")
        
        if failed_stocks:
            print(f"Failed stocks: {', '.join(failed_stocks)}")
        
        # Store results in XCom for downstream tasks
        context['task_instance'].xcom_push(
            key='crawl_results',
            value={
                'execution_date': execution_date,
                'total_stocks': total_stocks,
                'success_count': success_count,
                'failed_count': len(failed_stocks),
                'failed_stocks': failed_stocks,
                'success_rate': success_rate
            }
        )
        
        # Fail task if success rate < 80%
        if success_rate < 80:
            raise Exception(f"OHLCV crawl success rate ({success_rate:.1f}%) below threshold (80%)")
        
        return f"OHLCV crawl completed with {success_rate:.1f}% success rate"
        
    except Exception as e:
        print(f"💥 Critical error in OHLCV crawl: {str(e)}")
        raise

def validate_data(**context):
    """Validate crawled OHLCV data"""
    try:
        import boto3
        from datetime import datetime
        
        execution_date = context['ds']
        crawl_results = context['task_instance'].xcom_pull(
            task_ids='crawl_ohlcv_task',
            key='crawl_results'
        )
        
        print(f"🔍 Validating OHLCV data for {execution_date}")
        
        # Check S3 for uploaded files
        s3_client = boto3.client('s3')
        bucket_name = 'bankanalystportfolio'
        
        uploaded_files = []
        try:
            prefix = f"raw/ohlcv/date={execution_date}/"
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                uploaded_files = [obj['Key'] for obj in response['Contents']]
                print(f"📁 Found {len(uploaded_files)} files on S3")
            else:
                print("⚠️ No files found on S3")
                
        except Exception as e:
            print(f"❌ Error checking S3: {str(e)}")
        
        # Validation summary
        expected_files = crawl_results['success_count']
        actual_files = len(uploaded_files)
        
        print(f"\n📊 Data Validation Summary:")
        print(f"Expected files: {expected_files}")
        print(f"Actual files: {actual_files}")
        print(f"Match: {'✅' if expected_files == actual_files else '❌'}")
        
        # Store validation results
        context['task_instance'].xcom_push(
            key='validation_results',
            value={
                'execution_date': execution_date,
                'expected_files': expected_files,
                'actual_files': actual_files,
                'files_match': expected_files == actual_files,
                'uploaded_files': uploaded_files
            }
        )
        
        return f"Data validation completed: {actual_files}/{expected_files} files"
        
    except Exception as e:
        print(f"💥 Error in data validation: {str(e)}")
        raise

# Default arguments
default_args = {
    'owner': 'banking-portfolio',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Define DAG
dag = DAG(
    'daily_stock_pipeline',
    default_args=default_args,
    description='Daily OHLCV data crawling pipeline',
    schedule_interval='0 7 * * 1-5',  # 7AM weekdays (after market close)
    catchup=False,
    max_active_runs=1,
    tags=['banking', 'ohlcv', 'daily']
)

# Task 1: Crawl OHLCV data
crawl_ohlcv_task = PythonOperator(
    task_id='crawl_ohlcv_task',
    python_callable=crawl_ohlcv_data,
    dag=dag,
    provide_context=True,
    execution_timeout=timedelta(hours=2)
)

# Task 2: Validate data
validate_data_task = PythonOperator(
    task_id='validate_data_task',
    python_callable=validate_data,
    dag=dag,
    provide_context=True,
    execution_timeout=timedelta(minutes=10)
)

# Task 3: Health check
health_check_task = BashOperator(
    task_id='health_check_task',
    bash_command="""
    echo "🏥 OHLCV Pipeline Health Check"
    echo "Execution Date: {{ ds }}"
    echo "DAG Run ID: {{ dag_run.run_id }}"
    echo "Task Instance: {{ task_instance.task_id }}"
    echo "Pipeline completed successfully ✅"
    """,
    dag=dag
)

# Task dependencies
crawl_ohlcv_task >> validate_data_task >> health_check_task