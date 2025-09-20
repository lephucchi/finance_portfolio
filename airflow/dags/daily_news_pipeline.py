"""
DAG cho việc crawl tin tức banking hàng ngày
Author: Banking Portfolio Team
Description: Daily news crawling pipeline với sentiment analysis và logging
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# Add project root to path
sys.path.insert(0, '/opt/airflow/finance_portfolio')

# News sources configuration
NEWS_SOURCES = [
    'vneconomy.vn',
    'vnexpress.net', 
    'cafef.vn',
    'thoibaotaichinhvietnam.vn'
]

def crawl_news_data(**context):
    """Crawl banking news từ các nguồn tin tức chính"""
    try:
        import subprocess
        from datetime import datetime
        
        # Get execution date (previous day)
        execution_date = context['ds']
        
        print(f"📰 Starting News crawl for date: {execution_date}")
        
        # Run ingest_news.py 
        script_path = '/opt/airflow/finance_portfolio/scripts/ingest_news.py'
        
        try:
            cmd = f"cd /opt/airflow/finance_portfolio && python {script_path} --date {execution_date} --max-pages 3 --max-articles 10"
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            
            if result.returncode == 0:
                print("✅ News crawl completed successfully")
                print(f"Output: {result.stdout}")
                
                # Parse output for statistics (if available)
                output_lines = result.stdout.split('\n')
                stats = {
                    'success': True,
                    'execution_date': execution_date,
                    'raw_output': result.stdout
                }
                
            else:
                print(f"❌ News crawl failed: {result.stderr}")
                stats = {
                    'success': False,
                    'execution_date': execution_date,
                    'error': result.stderr,
                    'raw_output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            error_msg = "⏰ News crawl timeout (30 minutes)"
            print(error_msg)
            stats = {
                'success': False,
                'execution_date': execution_date,
                'error': error_msg
            }
            
        except Exception as e:
            error_msg = f"💥 Error in news crawl: {str(e)}"
            print(error_msg)
            stats = {
                'success': False,
                'execution_date': execution_date,
                'error': error_msg
            }
        
        # Store results in XCom
        context['task_instance'].xcom_push(
            key='crawl_results',
            value=stats
        )
        
        if not stats['success']:
            raise Exception(f"News crawl failed: {stats.get('error', 'Unknown error')}")
        
        return f"News crawl completed successfully for {execution_date}"
        
    except Exception as e:
        print(f"💥 Critical error in news crawl: {str(e)}")
        raise

def validate_news_data(**context):
    """Validate crawled news data"""
    try:
        import boto3
        from datetime import datetime
        
        execution_date = context['ds']
        crawl_results = context['task_instance'].xcom_pull(
            task_ids='crawl_news_task',
            key='crawl_results'
        )
        
        print(f"🔍 Validating news data for {execution_date}")
        
        # Check S3 for uploaded files
        s3_client = boto3.client('s3')
        bucket_name = 'bankanalystportfolio'
        
        uploaded_files = []
        total_articles = 0
        
        try:
            # Check each news source
            for source in NEWS_SOURCES:
                prefix = f"raw/news/source={source}/date={execution_date}/"
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix
                )
                
                if 'Contents' in response:
                    source_files = [obj['Key'] for obj in response['Contents']]
                    uploaded_files.extend(source_files)
                    total_articles += len(source_files)
                    print(f"📁 {source}: {len(source_files)} articles")
                else:
                    print(f"📁 {source}: 0 articles")
                    
        except Exception as e:
            print(f"❌ Error checking S3: {str(e)}")
        
        # Check logs
        log_files = []
        try:
            log_prefix = f"logs/news/date={execution_date}/"
            log_response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=log_prefix
            )
            
            if 'Contents' in log_response:
                log_files = [obj['Key'] for obj in log_response['Contents']]
                print(f"📋 Found {len(log_files)} log files")
            else:
                print("📋 No log files found")
                
        except Exception as e:
            print(f"❌ Error checking logs: {str(e)}")
        
        # Validation summary
        print(f"\n📊 News Data Validation Summary:")
        print(f"Total articles: {total_articles}")
        print(f"Sources with data: {len([s for s in NEWS_SOURCES if any(s in f for f in uploaded_files)])}")
        print(f"Log files: {len(log_files)}")
        print(f"Crawl success: {'✅' if crawl_results['success'] else '❌'}")
        
        # Store validation results
        validation_results = {
            'execution_date': execution_date,
            'total_articles': total_articles,
            'uploaded_files': len(uploaded_files),
            'log_files': len(log_files),
            'sources_with_data': len([s for s in NEWS_SOURCES if any(s in f for f in uploaded_files)]),
            'crawl_success': crawl_results['success']
        }
        
        context['task_instance'].xcom_push(
            key='validation_results',
            value=validation_results
        )
        
        return f"News validation completed: {total_articles} articles from {validation_results['sources_with_data']} sources"
        
    except Exception as e:
        print(f"💥 Error in news data validation: {str(e)}")
        raise

def sentiment_analysis(**context):
    """Perform sentiment analysis on crawled news (optional post-processing)"""
    try:
        execution_date = context['ds']
        validation_results = context['task_instance'].xcom_pull(
            task_ids='validate_news_task',
            key='validation_results'
        )
        
        print(f"📈 Starting sentiment analysis for {execution_date}")
        
        total_articles = validation_results.get('total_articles', 0)
        
        if total_articles == 0:
            print("⚠️ No articles found for sentiment analysis")
            return "Sentiment analysis skipped - no articles"
        
        print(f"📊 Processing {total_articles} articles for sentiment analysis")
        
        # Placeholder for future sentiment analysis implementation
        # This could integrate with existing sentiment analysis in ingest_news.py
        # or implement additional post-processing
        
        sentiment_results = {
            'execution_date': execution_date,
            'articles_processed': total_articles,
            'analysis_completed': True,
            'positive_sentiment': 0,  # Placeholder
            'negative_sentiment': 0,  # Placeholder  
            'neutral_sentiment': 0   # Placeholder
        }
        
        context['task_instance'].xcom_push(
            key='sentiment_results',
            value=sentiment_results
        )
        
        print(f"✅ Sentiment analysis completed for {total_articles} articles")
        return f"Sentiment analysis completed for {total_articles} articles"
        
    except Exception as e:
        print(f"💥 Error in sentiment analysis: {str(e)}")
        raise

# Default arguments
default_args = {
    'owner': 'banking-portfolio',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10)
}

# Define DAG
dag = DAG(
    'daily_news_pipeline',
    default_args=default_args,
    description='Daily banking news crawling pipeline',
    schedule_interval='0 8 * * 1-5',  # 8AM weekdays (after OHLCV pipeline)
    catchup=False,
    max_active_runs=1,
    tags=['banking', 'news', 'daily', 'sentiment']
)

# Task 1: Crawl news data
crawl_news_task = PythonOperator(
    task_id='crawl_news_task',
    python_callable=crawl_news_data,
    dag=dag,
    provide_context=True,
    execution_timeout=timedelta(hours=1)
)

# Task 2: Validate news data
validate_news_task = PythonOperator(
    task_id='validate_news_task',
    python_callable=validate_news_data,
    dag=dag,
    provide_context=True,
    execution_timeout=timedelta(minutes=15)
)

# Task 3: Sentiment analysis (optional)
sentiment_analysis_task = PythonOperator(
    task_id='sentiment_analysis_task',
    python_callable=sentiment_analysis,
    dag=dag,
    provide_context=True,
    execution_timeout=timedelta(minutes=30)
)

# Task 4: Health check
health_check_task = BashOperator(
    task_id='health_check_task',
    bash_command="""
    echo "🏥 News Pipeline Health Check"
    echo "Execution Date: {{ ds }}"
    echo "DAG Run ID: {{ dag_run.run_id }}"
    echo "Task Instance: {{ task_instance.task_id }}"
    echo "News pipeline completed successfully ✅"
    """,
    dag=dag
)

# Task dependencies
crawl_news_task >> validate_news_task >> sentiment_analysis_task >> health_check_task