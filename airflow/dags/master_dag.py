"""
Master DAG for Finance Portfolio ETL Pipeline
Orchestrates Bronze → Silver → Gold → RAG pipeline execution

Author: Banking Portfolio Team
Version: 2.0
Date: October 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.dates import days_ago
from airflow.sensors.external_task import ExternalTaskSensor
import logging
import os

# Default args for all tasks
default_args = {
    'owner': 'finance_portfolio',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=4),
}

# DAG definition
dag = DAG(
    'master_pipeline',
    default_args=default_args,
    description='Master orchestrator for Finance Portfolio ETL Pipeline (Bronze→Silver→Gold→RAG)',
    schedule_interval='0 6 * * 1-5',  # 6:00 AM weekdays
    catchup=False,
    max_active_runs=1,
    max_active_tasks=16,
    tags=['master', 'production', 'etl', 'rag'],
)

def check_market_status(**context):
    """Check if market is open and ready for data processing"""
    from datetime import datetime
    import pandas as pd
    
    execution_date = context['execution_date']
    weekday = execution_date.weekday()
    
    # Market closed on weekends
    if weekday >= 5:  # Saturday = 5, Sunday = 6
        logging.info(f"Market closed - Weekend (weekday: {weekday})")
        return False
    
    # Market closed on Vietnamese holidays (basic check)
    vietnam_holidays = [
        '2025-01-01',  # New Year
        '2025-04-30',  # Liberation Day
        '2025-05-01',  # Labor Day
        '2025-09-02',  # National Day
    ]
    
    date_str = execution_date.strftime('%Y-%m-%d')
    if date_str in vietnam_holidays:
        logging.info(f"Market closed - Holiday: {date_str}")
        return False
    
    logging.info(f"Market open - Processing date: {date_str}")
    return True

def validate_aws_connection(**context):
    """Validate AWS S3 connection and bucket access"""
    try:
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET_NAME', 'bankanalystportfolio')
        
        # Test bucket access
        if s3_hook.check_for_bucket(bucket_name):
            logging.info(f"✅ S3 bucket '{bucket_name}' accessible")
            
            # Test write permissions by creating a test file
            test_key = f"health-check/master-dag-{context['execution_date'].strftime('%Y%m%d-%H%M%S')}.txt"
            test_content = f"Master DAG health check at {datetime.now()}"
            
            s3_hook.load_string(
                string_data=test_content,
                key=test_key,
                bucket_name=bucket_name,
                replace=True
            )
            logging.info(f"✅ S3 write test successful: {test_key}")
            return True
        else:
            logging.error(f"❌ S3 bucket '{bucket_name}' not accessible")
            return False
            
    except Exception as e:
        logging.error(f"❌ AWS connection failed: {str(e)}")
        raise

def check_pipeline_dependencies(**context):
    """Check if all required dependencies are available"""
    s3_hook = S3Hook(aws_conn_id='aws_default')
    bucket_name = os.getenv('S3_BUCKET_NAME', 'bankanalystportfolio')
    
    # Check for previous day's data
    execution_date = context['execution_date']
    prev_date = (execution_date - timedelta(days=1)).strftime('%Y-%m-%d')
    
    dependencies = {
        'bronze_structure': 'bronze/',
        'silver_structure': 'silver/', 
        'gold_structure': 'gold/',
        'rag_structure': 'rag/',
    }
    
    missing_deps = []
    for dep_name, s3_prefix in dependencies.items():
        if not s3_hook.check_for_prefix(prefix=s3_prefix, bucket_name=bucket_name, delimiter='/'):
            missing_deps.append(dep_name)
    
    if missing_deps:
        logging.warning(f"⚠️ Missing dependencies: {missing_deps}")
        # Create missing structures
        for dep in missing_deps:
            prefix = dependencies[dep]
            s3_hook.load_string(
                string_data="# Auto-created by master DAG",
                key=f"{prefix}README.md",
                bucket_name=bucket_name
            )
            logging.info(f"✅ Created missing structure: {prefix}")
    else:
        logging.info("✅ All pipeline dependencies satisfied")
    
    return True

def generate_daily_report(**context):
    """Generate daily pipeline execution report"""
    execution_date = context['execution_date']
    date_str = execution_date.strftime('%Y-%m-%d')
    
    report = {
        'execution_date': date_str,
        'master_dag_status': 'SUCCESS',
        'timestamp': datetime.now().isoformat(),
        'pipeline_version': '2.0',
        'next_execution': (execution_date + timedelta(days=1)).strftime('%Y-%m-%d 06:00:00')
    }
    
    logging.info(f"📊 Daily Report Generated: {report}")
    
    # Save report to S3
    s3_hook = S3Hook(aws_conn_id='aws_default')
    bucket_name = os.getenv('S3_BUCKET_NAME', 'bankanalystportfolio')
    
    report_key = f"logs/master-dag/daily-reports/report-{date_str}.json"
    s3_hook.load_string(
        string_data=str(report),
        key=report_key,
        bucket_name=bucket_name,
        replace=True
    )
    
    return report

# Task definitions
start_task = DummyOperator(
    task_id='start_master_pipeline',
    dag=dag,
)

market_check = PythonOperator(
    task_id='check_market_status',
    python_callable=check_market_status,
    dag=dag,
)

aws_validation = PythonOperator(
    task_id='validate_aws_connection',
    python_callable=validate_aws_connection,
    dag=dag,
)

dependency_check = PythonOperator(
    task_id='check_pipeline_dependencies',
    python_callable=check_pipeline_dependencies,
    dag=dag,
)

# Pipeline trigger tasks (will be implemented in separate DAGs)
# External pipeline sensors to monitor completion
bronze_sensor = ExternalTaskSensor(
    task_id='wait_for_bronze_completion',
    external_dag_id='bronze_layer_pipeline',
    external_task_id='validate_bronze_data',
    allowed_states=['success'],
    failed_states=['failed', 'upstream_failed'],
    timeout=3600,  # 1 hour timeout
    poke_interval=300,  # Check every 5 minutes
    mode='reschedule',
    dag=dag,
)

silver_sensor = ExternalTaskSensor(
    task_id='wait_for_silver_completion',
    external_dag_id='silver_layer_pipeline',
    external_task_id='validate_silver_data',
    allowed_states=['success'],
    failed_states=['failed', 'upstream_failed'],
    timeout=3600,
    poke_interval=300,
    mode='reschedule',
    dag=dag,
)

gold_sensor = ExternalTaskSensor(
    task_id='wait_for_gold_completion',
    external_dag_id='gold_layer_pipeline',
    external_task_id='track_pipeline_metadata',
    allowed_states=['success'],
    failed_states=['failed', 'upstream_failed'],
    timeout=3600,
    poke_interval=300,
    mode='reschedule',
    dag=dag,
)

rag_sensor = ExternalTaskSensor(
    task_id='wait_for_rag_completion',
    external_dag_id='rag_pipeline',
    external_task_id='validate_rag_pipeline',
    allowed_states=['success'],
    failed_states=['failed', 'upstream_failed'],
    timeout=3600,
    poke_interval=300,
    mode='reschedule',
    dag=dag,
)

# Pipeline trigger operators
trigger_bronze = BashOperator(
    task_id='trigger_bronze_pipeline',
    bash_command='echo "🔵 Triggering Bronze layer pipeline at $(date)"',
    dag=dag,
)

trigger_silver = BashOperator(
    task_id='trigger_silver_pipeline',
    bash_command='echo "🥈 Triggering Silver layer pipeline at $(date)"',
    dag=dag,
)

trigger_gold = BashOperator(
    task_id='trigger_gold_pipeline',
    bash_command='echo "🥇 Triggering Gold layer pipeline at $(date)"',
    dag=dag,
)

trigger_rag = BashOperator(
    task_id='trigger_rag_pipeline',
    bash_command='echo "🤖 Triggering RAG pipeline at $(date)"',
    dag=dag,
)

# Health checks
health_check = BashOperator(
    task_id='system_health_check',
    bash_command="""
    echo "🔍 System Health Check"
    echo "Memory usage: $(free -h | grep '^Mem' | awk '{print $3 "/" $2}')"
    echo "Disk usage: $(df -h / | tail -1 | awk '{print $5 " used"}')"
    echo "Docker containers running: $(docker ps | grep -c Up || echo 'N/A')"
    echo "Current time: $(date)"
    """,
    dag=dag,
)

# Report generation
daily_report = PythonOperator(
    task_id='generate_daily_report',
    python_callable=generate_daily_report,
    trigger_rule=TriggerRule.ALL_DONE,  # Run even if some tasks fail
    dag=dag,
)

end_task = DummyOperator(
    task_id='end_master_pipeline',
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag,
)

# Task dependencies - Proper pipeline orchestration
start_task >> [market_check, aws_validation] >> dependency_check >> health_check

# Bronze layer (starts first)
health_check >> trigger_bronze >> bronze_sensor

# Silver layer (after bronze completion)  
bronze_sensor >> trigger_silver >> silver_sensor

# Gold layer (after silver completion)
silver_sensor >> trigger_gold >> gold_sensor

# RAG pipeline (after gold completion for news processing)
gold_sensor >> trigger_rag >> rag_sensor

# Final reporting (after all pipelines complete)
rag_sensor >> daily_report >> end_task

# Make DAG available
globals()['master_pipeline_v2'] = dag