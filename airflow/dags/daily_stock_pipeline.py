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

def crawl_ohlcv():
    """Crawl OHLCV data for banking stocks"""
    import os
    import pandas as pd
    import vnstock
    import boto3
    from datetime import datetime, timedelta
    
    # Banking stocks list
    banking_stocks = [
        'TCB', 'VCB', 'CTG', 'BID', 'VPB', 'MBB', 'ACB', 'STB', 
        'HDB', 'TPB', 'EIB', 'MSB', 'SHB', 'OCB', 'VIB', 'LPB',
        'KLB', 'NAB', 'PGB', 'VAB', 'ABB', 'BAB', 'BVB', 'CBB',
        'IVB', 'NVB', 'PVcomBank'
    ]
    
    try:
        # Get yesterday's date
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        
        all_data = []
        success_count = 0
        
        for symbol in banking_stocks:
            try:
                # Get OHLCV data using vnstock legacy API
                data = vnstock.stock_historical_data(
                    symbol=symbol,
                    start_date=yesterday,
                    end_date=today,
                    resolution='1D',
                    type='stock',
                    beautify=True,
                    source='DNSE'
                )
                
                if not data.empty:
                    data['symbol'] = symbol
                    data['date'] = yesterday
                    all_data.append(data)
                    success_count += 1
                    print(f"✅ {symbol}: {len(data)} records")
                else:
                    print(f"❌ {symbol}: No data")
                    
            except Exception as e:
                print(f"❌ {symbol}: {str(e)}")
        
        if all_data:
            # Combine all data
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Upload to S3
            s3_client = boto3.client('s3')
            csv_buffer = combined_df.to_csv(index=False)
            
            s3_key = f"raw/stocks/ohlcv/date={yesterday}/banking_stocks.csv"
            s3_client.put_object(
                Bucket=os.getenv('AWS_S3_BUCKET'),
                Key=s3_key,
                Body=csv_buffer
            )
            
            print(f"✅ Uploaded {len(combined_df)} records to S3: {s3_key}")
            print(f"✅ Success rate: {success_count}/{len(banking_stocks)} ({success_count/len(banking_stocks)*100:.1f}%)")
        else:
            raise Exception("No data crawled for any stocks")
            
    except Exception as e:
        print(f"❌ OHLCV crawling failed: {str(e)}")
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
    python_callable=crawl_ohlcv,
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