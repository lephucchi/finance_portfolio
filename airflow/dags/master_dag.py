"""
Master DAG - Orchestrator cho Banking Portfolio Pipeline
Author: Banking Portfolio Team
Description: Điều phối và monitor cả OHLCV và News pipelines
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
# from airflow.operators.dagrun_operator import TriggerDagRunOperator  # Will be replaced with BashOperator
import sys
import os

# Add project root to path
sys.path.insert(0, '/opt/airflow/finance_portfolio')

def pipeline_orchestrator(**context):
    """Main orchestrator function"""
    try:
        execution_date = context['ds']
        print(f"🎯 Starting Banking Portfolio Pipeline for {execution_date}")
        
        # Pipeline configuration
        pipeline_config = {
            'execution_date': execution_date,
            'ohlcv_dag': 'daily_stock_pipeline',
            'news_dag': 'daily_news_pipeline',
            'max_wait_time': 14400,  # 4 hours
            'retry_attempts': 2
        }
        
        print(f"📋 Pipeline Configuration:")
        for key, value in pipeline_config.items():
            print(f"  {key}: {value}")
        
        # Store config in XCom for downstream tasks
        context['task_instance'].xcom_push(
            key='pipeline_config',
            value=pipeline_config
        )
        
        return f"Pipeline orchestrator initialized for {execution_date}"
        
    except Exception as e:
        print(f"💥 Error in pipeline orchestrator: {str(e)}")
        raise

def check_market_status(**context):
    """Check if market is open (weekdays only)"""
    try:
        from datetime import datetime
        
        execution_date = context['ds']
        date_obj = datetime.strptime(execution_date, '%Y-%m-%d')
        weekday = date_obj.weekday()
        
        # 0=Monday, 6=Sunday
        is_weekday = weekday < 5
        
        print(f"📅 Date: {execution_date} (weekday: {weekday})")
        print(f"📈 Market Status: {'Open' if is_weekday else 'Closed'}")
        
        market_status = {
            'execution_date': execution_date,
            'weekday': weekday,
            'is_market_open': is_weekday,
            'should_run_pipeline': is_weekday
        }
        
        context['task_instance'].xcom_push(
            key='market_status',
            value=market_status
        )
        
        if not is_weekday:
            print("⚠️ Market closed - skipping pipeline execution")
            return "Market closed - pipeline skipped"
        
        return f"Market open - proceeding with pipeline for {execution_date}"
        
    except Exception as e:
        print(f"💥 Error checking market status: {str(e)}")
        raise

def monitor_pipelines(**context):
    """Monitor execution của cả 2 sub-pipelines"""
    try:
        import boto3
        from datetime import datetime
        
        execution_date = context['ds']
        
        print(f"📊 Monitoring pipelines for {execution_date}")
        
        # Get pipeline status from logs
        s3_client = boto3.client('s3')
        bucket_name = 'bankanalystportfolio'
        
        # Check OHLCV logs
        ohlcv_logs = []
        news_logs = []
        
        try:
            # OHLCV logs
            ohlcv_prefix = f"logs/ohlcv/date={execution_date}/"
            ohlcv_response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=ohlcv_prefix
            )
            
            if 'Contents' in ohlcv_response:
                ohlcv_logs = [obj['Key'] for obj in ohlcv_response['Contents']]
            
            # News logs  
            news_prefix = f"logs/news/date={execution_date}/"
            news_response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=news_prefix
            )
            
            if 'Contents' in news_response:
                news_logs = [obj['Key'] for obj in news_response['Contents']]
                
        except Exception as e:
            print(f"❌ Error accessing S3 logs: {str(e)}")
        
        # Check data files
        ohlcv_files = []
        news_files = []
        
        try:
            # OHLCV data files
            ohlcv_data_prefix = f"raw/ohlcv/date={execution_date}/"
            ohlcv_data_response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=ohlcv_data_prefix
            )
            
            if 'Contents' in ohlcv_data_response:
                ohlcv_files = [obj['Key'] for obj in ohlcv_data_response['Contents']]
            
            # News data files (all sources)
            news_sources = ['vneconomy.vn', 'vnexpress.net', 'cafef.vn', 'thoibaotaichinhvietnam.vn']
            for source in news_sources:
                news_data_prefix = f"raw/news/source={source}/date={execution_date}/"
                news_data_response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=news_data_prefix
                )
                
                if 'Contents' in news_data_response:
                    news_files.extend([obj['Key'] for obj in news_data_response['Contents']])
                    
        except Exception as e:
            print(f"❌ Error accessing S3 data: {str(e)}")
        
        # Generate monitoring report
        monitoring_report = {
            'execution_date': execution_date,
            'timestamp': datetime.now().isoformat(),
            'ohlcv_pipeline': {
                'log_files': len(ohlcv_logs),
                'data_files': len(ohlcv_files),
                'status': 'completed' if ohlcv_logs and ohlcv_files else 'incomplete'
            },
            'news_pipeline': {
                'log_files': len(news_logs),
                'data_files': len(news_files),
                'status': 'completed' if news_logs and news_files else 'incomplete'
            },
            'overall_status': 'success' if (ohlcv_logs and ohlcv_files and news_logs) else 'partial'
        }
        
        print(f"\n📊 Pipeline Monitoring Report:")
        print(f"🏦 OHLCV Pipeline:")
        print(f"  └── Log files: {monitoring_report['ohlcv_pipeline']['log_files']}")
        print(f"  └── Data files: {monitoring_report['ohlcv_pipeline']['data_files']}")
        print(f"  └── Status: {monitoring_report['ohlcv_pipeline']['status']}")
        
        print(f"📰 News Pipeline:")
        print(f"  └── Log files: {monitoring_report['news_pipeline']['log_files']}")
        print(f"  └── Data files: {monitoring_report['news_pipeline']['data_files']}")
        print(f"  └── Status: {monitoring_report['news_pipeline']['status']}")
        
        print(f"🎯 Overall Status: {monitoring_report['overall_status']}")
        
        # Store monitoring results
        context['task_instance'].xcom_push(
            key='monitoring_report',
            value=monitoring_report
        )
        
        return f"Pipeline monitoring completed - Status: {monitoring_report['overall_status']}"
        
    except Exception as e:
        print(f"💥 Error in pipeline monitoring: {str(e)}")
        raise

def generate_daily_report(**context):
    """Generate daily summary report"""
    try:
        execution_date = context['ds']
        
        # Get monitoring report
        monitoring_report = context['task_instance'].xcom_pull(
            task_ids='monitor_pipelines_task',
            key='monitoring_report'
        )
        
        # Get market status
        market_status = context['task_instance'].xcom_pull(
            task_ids='check_market_task',
            key='market_status'
        )
        
        print(f"📋 Generating daily report for {execution_date}")
        
        # Create comprehensive report
        daily_report = {
            'report_date': execution_date,
            'report_timestamp': datetime.now().isoformat(),
            'market_info': market_status,
            'pipeline_results': monitoring_report,
            'summary': {
                'market_open': market_status.get('is_market_open', False),
                'ohlcv_success': monitoring_report['ohlcv_pipeline']['status'] == 'completed',
                'news_success': monitoring_report['news_pipeline']['status'] == 'completed',
                'overall_success': monitoring_report['overall_status'] == 'success'
            }
        }
        
        print(f"\n📊 Daily Report Summary:")
        print(f"📅 Date: {execution_date}")
        print(f"📈 Market: {'Open' if daily_report['summary']['market_open'] else 'Closed'}")
        print(f"🏦 OHLCV: {'✅' if daily_report['summary']['ohlcv_success'] else '❌'}")
        print(f"📰 News: {'✅' if daily_report['summary']['news_success'] else '❌'}")
        print(f"🎯 Overall: {'✅' if daily_report['summary']['overall_success'] else '❌'}")
        
        # Store final report
        context['task_instance'].xcom_push(
            key='daily_report',
            value=daily_report
        )
        
        return f"Daily report generated for {execution_date}"
        
    except Exception as e:
        print(f"💥 Error generating daily report: {str(e)}")
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

# Define Master DAG
dag = DAG(
    'master_dag',
    default_args=default_args,
    description='Master orchestrator for Banking Portfolio Pipeline',
    schedule_interval='0 6 * * 1-5',  # 6AM weekdays (before sub-pipelines)
    catchup=False,
    max_active_runs=1,
    tags=['banking', 'master', 'orchestrator']
)

# Task 1: Initialize orchestrator
init_orchestrator_task = PythonOperator(
    task_id='init_orchestrator_task',
    python_callable=pipeline_orchestrator,
    dag=dag,
    provide_context=True
)

# Task 2: Check market status
check_market_task = PythonOperator(
    task_id='check_market_task',
    python_callable=check_market_status,
    dag=dag,
    provide_context=True
)

# Task 3: Trigger OHLCV pipeline
trigger_ohlcv_task = BashOperator(
    task_id='trigger_ohlcv_task',
    bash_command='airflow dags trigger daily_stock_pipeline',
    dag=dag
)

# Task 4: Trigger News pipeline  
trigger_news_task = BashOperator(
    task_id='trigger_news_task',
    bash_command='airflow dags trigger daily_news_pipeline',
    dag=dag
)

# Task 5: Wait for OHLCV completion
wait_ohlcv_task = ExternalTaskSensor(
    task_id='wait_ohlcv_task',
    external_dag_id='daily_stock_pipeline',
    external_task_id='health_check_task',
    dag=dag,
    timeout=14400,  # 4 hours
    poke_interval=300,  # 5 minutes
    mode='poke'
)

# Task 6: Wait for News completion
wait_news_task = ExternalTaskSensor(
    task_id='wait_news_task',
    external_dag_id='daily_news_pipeline',
    external_task_id='health_check_task',
    dag=dag,
    timeout=14400,  # 4 hours  
    poke_interval=300,  # 5 minutes
    mode='poke'
)

# Task 7: Monitor pipelines
monitor_pipelines_task = PythonOperator(
    task_id='monitor_pipelines_task',
    python_callable=monitor_pipelines,
    dag=dag,
    provide_context=True
)

# Task 8: Generate daily report
daily_report_task = PythonOperator(
    task_id='daily_report_task',
    python_callable=generate_daily_report,
    dag=dag,
    provide_context=True
)

# Task 9: Final health check
final_health_check_task = BashOperator(
    task_id='final_health_check_task',
    bash_command="""
    echo "🏥 Master Pipeline Health Check"
    echo "Execution Date: {{ ds }}"
    echo "DAG Run ID: {{ dag_run.run_id }}"
    echo "Master pipeline orchestration completed ✅"
    """,
    dag=dag
)

# Task dependencies
init_orchestrator_task >> check_market_task

# Parallel execution of sub-pipelines
check_market_task >> [trigger_ohlcv_task, trigger_news_task]

# Wait for both pipelines to complete
trigger_ohlcv_task >> wait_ohlcv_task
trigger_news_task >> wait_news_task

# Final monitoring and reporting
[wait_ohlcv_task, wait_news_task] >> monitor_pipelines_task >> daily_report_task >> final_health_check_task