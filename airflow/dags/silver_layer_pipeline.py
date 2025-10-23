"""
Silver Layer Pipeline - Production Ready
=========================================================================
Process Bronze layer data from TODAY and write to Silver layer with:
- Parquet format with Snappy compression
- Hive-style partitioning: partition_date=YYYY-MM-DD
- Standard Python logging (no enhanced_logger dependency)
- Only processes data from execution date (no historical backfill)

Schedule: Daily at 7 AM (weekdays), after Bronze layer
Dependencies: pandas, pyarrow, boto3
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
import json
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
import io
import sys

# Import sentiment analyzer
sys.path.append('/opt/airflow/dags')
from utils.sentiment_analyzer import calculate_sentiment_score, classify_sentiment

# Default arguments
default_args = {
    'owner': 'finance_portfolio',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# DAG definition
dag = DAG(
    'silver_layer_pipeline',
    default_args=default_args,
    description='Silver layer data processing (Bronze → Parquet)',
    schedule_interval='0 7 * * 1-5',  # 7 AM weekdays
    catchup=False,
    tags=['silver', 'lakehouse', 'parquet'],
    max_active_runs=1
)


def process_stock_data(**context):
    """
    Process stock data from Bronze (today only)
    Input: bronze/stocks/raw/{ticker}_{date}.json
    Output: silver/stocks/partition_date=YYYY-MM-DD/stock_data.parquet
    """
    logger = logging.getLogger(__name__)
    
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger.info(f"📈 Processing stocks for {date_str}")
        
        # S3 setup
        s3 = boto3.client('s3')
        bucket = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # List Bronze stock files for TODAY only
        logger.info(f"📂 Listing Bronze stock files for {date_str}...")
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=f'bronze/stocks/raw/')
        
        stock_files = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'].endswith('.json') and date_str in obj['Key']:
                        stock_files.append(obj['Key'])
        
        if not stock_files:
            logger.warning(f"⚠️ No stock files found for {date_str}")
            return {'status': 'no_data', 'date': date_str, 'files': 0}
        
        logger.info(f"📊 Found {len(stock_files)} stock files")
        
        # Read and combine all files
        all_records = []
        errors = 0
        
        for key in stock_files:
            try:
                obj = s3.get_object(Bucket=bucket, Key=key)
                data = json.loads(obj['Body'].read().decode('utf-8'))
                
                ticker = data.get('ticker', '')
                for record in data.get('data', []):
                    record['ticker'] = ticker
                    record['_source'] = data.get('_source', 'vnstock_v3')
                    all_records.append(record)
            except Exception as e:
                errors += 1
                logger.error(f"Error reading {key}: {e}")
        
        if not all_records:
            logger.warning("⚠️ No valid records extracted")
            return {'status': 'no_records', 'date': date_str, 'files': len(stock_files), 'errors': errors}
        
        logger.info(f"📦 Processing {len(all_records)} records from {len(stock_files)} files ({errors} errors)")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_records)
        df['partition_date'] = date_str
        
        # Write Parquet to S3
        table = pa.Table.from_pandas(df)
        output_key = f'silver/stocks/partition_date={date_str}/stock_data.parquet'
        
        buf = io.BytesIO()
        pq.write_table(table, buf, compression='snappy')
        buf.seek(0)
        
        s3.put_object(Bucket=bucket, Key=output_key, Body=buf.getvalue())
        
        parquet_size = len(buf.getvalue()) / 1024
        logger.info(f"✅ SUCCESS: {len(all_records)} records → {output_key}")
        logger.info(f"   Parquet size: {parquet_size:.1f} KB | Tickers: {df['ticker'].nunique()}")
        
        return {
            'status': 'success',
            'date': date_str,
            'files_read': len(stock_files),
            'records': len(all_records),
            'tickers': int(df['ticker'].nunique()),
            'output': output_key,
            'size_kb': round(parquet_size, 1),
            'errors': errors
        }
        
    except Exception as e:
        logger.error(f"💥 STOCK PROCESSING FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def process_news_data(**context):
    """
    Process news data from Bronze (recent files only)
    Input: bronze/news/raw/{id}.json
    Output: silver/news/partition_date=YYYY-MM-DD/news_cleaned.parquet
    """
    logger = logging.getLogger(__name__)
    
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger.info(f"📰 Processing news for {date_str}")
        
        # S3 setup
        s3 = boto3.client('s3')
        bucket = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # List Bronze news files (filter by modification time)
        logger.info(f"📂 Listing recent Bronze news files...")
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=f'bronze/news/raw/')
        
        # Get files modified in last 24 hours
        cutoff_time = execution_date - timedelta(hours=24)
        recent_files = []
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'].endswith('.json') and obj['LastModified'] >= cutoff_time:
                        recent_files.append(obj['Key'])
        
        if not recent_files:
            logger.warning(f"⚠️ No recent news files found")
            return {'status': 'no_data', 'date': date_str, 'files': 0}
        
        logger.info(f"📊 Found {len(recent_files)} recent news files")
        
        # Read and combine with content and sentiment
        all_records = []
        errors = 0
        
        for key in recent_files:
            try:
                obj = s3.get_object(Bucket=bucket, Key=key)
                data = json.loads(obj['Body'].read().decode('utf-8'))
                
                # Extract content (combined_text or title)
                content = data.get('combined_text', '') or data.get('title', '')
                title = data.get('title', '')
                
                # Calculate sentiment score
                full_text = f"{title} {content}"
                sentiment_score = calculate_sentiment_score(full_text)
                sentiment_category = classify_sentiment(sentiment_score)
                
                record = {
                    'title': title,
                    'content': content[:500] if content else '',  # Limit to 500 chars
                    'link': data.get('link', ''),
                    'source': data.get('source', ''),
                    'published_date': data.get('published_date', ''),
                    'extraction_method': data.get('extraction_method', ''),
                    'sentiment_score': sentiment_score,
                    'sentiment_category': sentiment_category,
                }
                all_records.append(record)
            except Exception as e:
                errors += 1
                logger.error(f"Error reading {key}: {e}")
        
        if not all_records:
            logger.warning("⚠️ No valid news records")
            return {'status': 'no_records', 'date': date_str, 'files': len(recent_files), 'errors': errors}
        
        logger.info(f"📦 Processing {len(all_records)} news records ({errors} errors)")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_records)
        df['partition_date'] = date_str
        
        # Write Parquet
        table = pa.Table.from_pandas(df)
        output_key = f'silver/news/partition_date={date_str}/news_cleaned.parquet'
        
        buf = io.BytesIO()
        pq.write_table(table, buf, compression='snappy')
        buf.seek(0)
        
        s3.put_object(Bucket=bucket, Key=output_key, Body=buf.getvalue())
        
        parquet_size = len(buf.getvalue()) / 1024
        logger.info(f"✅ SUCCESS: {len(all_records)} records → {output_key}")
        logger.info(f"   Parquet size: {parquet_size:.1f} KB | Sources: {df['source'].nunique()}")
        logger.info(f"   Sentiment: avg={df['sentiment_score'].mean():.2f}, positive={len(df[df['sentiment_score']>0])}, negative={len(df[df['sentiment_score']<0])}")
        
        return {
            'status': 'success',
            'date': date_str,
            'files_read': len(recent_files),
            'records': len(all_records),
            'sources': int(df['source'].nunique()),
            'output': output_key,
            'size_kb': round(parquet_size, 1),
            'errors': errors,
            'avg_sentiment': round(df['sentiment_score'].mean(), 2)
        }
        
    except Exception as e:
        logger.error(f"💥 NEWS PROCESSING FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def process_macro_data(**context):
    """
    Process macro data from Bronze (all indicators)
    Input: bronze/macro/raw/{category}/{indicator}.csv
    Output: silver/macro/partition_date=YYYY-MM-DD/macro_data.parquet
    """
    logger = logging.getLogger(__name__)
    
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger.info(f"📊 Processing macro for {date_str}")
        
        # S3 setup
        s3 = boto3.client('s3')
        bucket = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # List Bronze macro files (all CSV files)
        logger.info(f"📂 Listing Bronze macro files...")
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=f'bronze/macro/raw/')
        
        csv_files = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'].endswith('.csv'):
                        csv_files.append(obj['Key'])
        
        if not csv_files:
            logger.warning(f"⚠️ No macro CSV files found")
            return {'status': 'no_data', 'date': date_str, 'files': 0}
        
        logger.info(f"📊 Found {len(csv_files)} macro CSV files")
        
        # Read and combine all CSVs
        all_dfs = []
        errors = 0
        
        for key in csv_files:
            try:
                obj = s3.get_object(Bucket=bucket, Key=key)
                df_temp = pd.read_csv(io.BytesIO(obj['Body'].read()))
                
                # Extract indicator name and category from path
                parts = key.split('/')
                indicator_name = parts[-1].replace('.csv', '')
                category = parts[-2] if len(parts) > 3 else 'unknown'
                
                df_temp['indicator'] = indicator_name
                df_temp['category'] = category
                
                all_dfs.append(df_temp)
            except Exception as e:
                errors += 1
                logger.error(f"Error reading {key}: {e}")
        
        if not all_dfs:
            logger.warning("⚠️ No valid macro records")
            return {'status': 'no_records', 'date': date_str, 'files': len(csv_files), 'errors': errors}
        
        # Combine all dataframes
        df = pd.concat(all_dfs, ignore_index=True)
        df['partition_date'] = date_str
        
        logger.info(f"📦 Processing {len(df)} macro records from {len(csv_files)} indicators ({errors} errors)")
        
        # Write Parquet
        table = pa.Table.from_pandas(df)
        output_key = f'silver/macro/partition_date={date_str}/macro_data.parquet'
        
        buf = io.BytesIO()
        pq.write_table(table, buf, compression='snappy')
        buf.seek(0)
        
        s3.put_object(Bucket=bucket, Key=output_key, Body=buf.getvalue())
        
        parquet_size = len(buf.getvalue()) / 1024
        logger.info(f"✅ SUCCESS: {len(df)} records → {output_key}")
        logger.info(f"   Parquet size: {parquet_size:.1f} KB | Indicators: {df['indicator'].nunique()}")
        
        return {
            'status': 'success',
            'date': date_str,
            'files_read': len(csv_files),
            'records': len(df),
            'indicators': int(df['indicator'].nunique()),
            'output': output_key,
            'size_kb': round(parquet_size, 1),
            'errors': errors
        }
        
    except Exception as e:
        logger.error(f"💥 MACRO PROCESSING FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def validate_silver_data(**context):
    """Validate Silver layer Parquet outputs exist"""
    logger = logging.getLogger(__name__)
    
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger.info(f"🔍 Validating Silver data for {date_str}")
        
        s3 = boto3.client('s3')
        bucket = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        validation_results = {
            'date': date_str,
            'stocks': {'exists': False, 'size_kb': 0},
            'news': {'exists': False, 'size_kb': 0},
            'macro': {'exists': False, 'size_kb': 0},
        }
        
        # Check each data type
        for data_type in ['stocks', 'news', 'macro']:
            key = f"silver/{data_type}/partition_date={date_str}/"
            try:
                resp = s3.list_objects_v2(Bucket=bucket, Prefix=key, MaxKeys=10)
                if 'Contents' in resp:
                    parquet_files = [obj for obj in resp['Contents'] if obj['Key'].endswith('.parquet')]
                    if parquet_files:
                        validation_results[data_type]['exists'] = True
                        validation_results[data_type]['size_kb'] = round(sum(obj['Size'] for obj in parquet_files) / 1024, 1)
                        logger.info(f"  ✅ {data_type}: {len(parquet_files)} file(s), {validation_results[data_type]['size_kb']} KB")
                    else:
                        logger.warning(f"  ⚠️ {data_type}: No parquet files found")
                else:
                    logger.warning(f"  ⚠️ {data_type}: Directory not found")
            except Exception as e:
                logger.error(f"  ❌ {data_type}: Validation error - {e}")
        
        logger.info(f"✅ Validation Complete")
        
        return validation_results
        
    except Exception as e:
        logger.error(f"💥 VALIDATION FAILED: {e}")
        raise


# Task definitions
process_stocks = PythonOperator(
    task_id='process_stock_data',
    python_callable=process_stock_data,
    dag=dag,
)

process_news = PythonOperator(
    task_id='process_news_data',
    python_callable=process_news_data,
    dag=dag,
)

process_macro = PythonOperator(
    task_id='process_macro_data',
    python_callable=process_macro_data,
    dag=dag,
)

validate_data = PythonOperator(
    task_id='validate_silver_data',
    python_callable=validate_silver_data,
    dag=dag,
)

# Task dependencies: All processing runs in parallel, then validation
[process_stocks, process_news, process_macro] >> validate_data
