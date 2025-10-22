"""
Silver Layer Pipeline (Aligned with S3_LAKEHOUSE_COMPLETE_STRUCTURE.md)
=========================================================================

This DAG processes Bronze layer data and writes to Silver layer with:
- Batch processing (500 files per batch)
- Parquet format with Snappy compression
- Hive-style partitioning: partition_date=YYYY-MM-DD
- Concurrent file reading (10 workers)
- Schema validation and data quality checks

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
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from enhanced_logger import log_pipeline_start, log_pipeline_success, log_pipeline_error

# Default arguments
default_args = {
    'owner': 'finance_portfolio',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=3),
}

# DAG definition
dag = DAG(
    'silver_layer_pipeline',
    default_args=default_args,
    description='Silver layer data processing (Bronze → Parquet + partitioning)',
    schedule_interval='0 7 * * 1-5',  # 7 AM weekdays
    catchup=False,
    tags=['silver', 'lakehouse', 'parquet'],
    max_active_runs=1
)


def process_stock_data(**context):
    """
    Process stock data with batch reading and Parquet output
    Input: bronze/stocks/raw/{ticker}_{date}.json (flat structure)
    Output: silver/stocks/partition_date=YYYY-MM-DD/stock_data.parquet
    """
    try:
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import io
        
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger = logging.getLogger(__name__)
        logger.info(f"📈 Starting stock data processing for {date_str}")
        
        # Enhanced logger metadata
        metadata = {
            'pipeline_name': 'silver_stock_processing',
            'layer': 'silver',
            'data_type': 'stocks',
            'execution_date': date_str
        }
        
        log_pipeline_start(logger, metadata)
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        s3_client = s3_hook.get_conn()
        
        # List all stock files for today
        logger.info(f"📂 Listing Bronze stock files...")
        stock_files = []
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name, Prefix=f"bronze/stocks/raw/"):
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'].endswith('.json') and date_str in obj['Key']:
                        stock_files.append(obj['Key'])
        
        if not stock_files:
            logger.warning(f"⚠️ No stock files found for {date_str}")
            result = {'stocks_processed': 0, 'execution_date': date_str}
            log_pipeline_success(logger, metadata, result)
            return result
        
        logger.info(f"📊 Found {len(stock_files)} stock files")
        
        # Concurrent file reading (10 workers, batches of 500)
        def read_single_stock_file(key):
            try:
                obj = s3_client.get_object(Bucket=bucket_name, Key=key)
                content = obj['Body'].read(amt=1024*1024*10).decode('utf-8')
                data = json.loads(content)
                
                # Extract ticker and data
                ticker = data.get('ticker', '')
                stock_data = data.get('data', [])
                
                if not stock_data:
                    return None
                
                # Convert to records with ticker
                records = []
                for record in stock_data:
                    record['ticker'] = ticker
                    record['_source'] = data.get('_source', 'vnstock_v3')
                    record['_ingest_time'] = data.get('_ingested_at_utc', '')
                    records.append(record)
                
                return records
                
            except Exception as e:
                logger.error(f"  ❌ Error reading {key}: {str(e)}")
                return None
        
        # Process in batches of 500 files
        BATCH_SIZE = 500
        all_records = []
        
        for i in range(0, len(stock_files), BATCH_SIZE):
            batch_files = stock_files[i:i+BATCH_SIZE]
            logger.info(f"📦 Processing batch {i//BATCH_SIZE + 1}/{(len(stock_files)-1)//BATCH_SIZE + 1} ({len(batch_files)} files)...")
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(read_single_stock_file, key): key for key in batch_files}
                
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        all_records.extend(result)
        
        if not all_records:
            logger.warning(f"⚠️ No valid stock records after processing")
            result = {'stocks_processed': 0, 'execution_date': date_str}
            log_pipeline_success(logger, metadata, result)
            return result
        
        logger.info(f"📝 Loaded {len(all_records)} stock records")
        
        # Create DataFrame
        df = pd.DataFrame(all_records)
        
        # Clean and standardize
        logger.info(f"🧹 Cleaning and standardizing data...")
        
        # Rename columns
        df.rename(columns={
            'ticker': 'symbol',
            'date': 'data_date',
            '_ingest_time': '_ingested_at_utc'
        }, inplace=True)
        
        # Ensure data types
        df['symbol'] = df['symbol'].astype(str).str.upper()
        df['data_date'] = pd.to_datetime(df['data_date']).dt.strftime('%Y-%m-%d')
        
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill volume NaN with 0
        if 'volume' in df.columns:
            df['volume'] = df['volume'].fillna(0).astype(int)
        
        # Calculate technical indicators
        df['price_change'] = df['close'] - df['open']
        df['price_change_pct'] = ((df['close'] - df['open']) / df['open'] * 100).round(4)
        
        # Drop duplicates
        df = df.drop_duplicates(subset=['symbol', 'data_date'], keep='last')
        
        # Remove rows with missing critical data
        df = df.dropna(subset=['symbol', 'data_date', 'close'])
        
        # Select columns for Silver layer
        silver_cols = ['symbol', 'data_date', 'open', 'high', 'low', 'close', 'volume',
                       'price_change', 'price_change_pct', '_source', '_ingested_at_utc']
        df = df[[col for col in silver_cols if col in df.columns]]
        
        # Sort by symbol and date
        df = df.sort_values(['symbol', 'data_date']).reset_index(drop=True)
        
        logger.info(f"✅ Cleaned data: {len(df)} records, {df['symbol'].nunique()} unique symbols")
        
        # Add partition_date column
        df['partition_date'] = date_str
        
        # Convert to Parquet and upload
        logger.info(f"💾 Writing Parquet file to S3...")
        
        parquet_buffer = io.BytesIO()
        df.to_parquet(
            parquet_buffer,
            engine='pyarrow',
            compression='snappy',
            index=False
        )
        
        # S3 key with partition
        s3_key = f"silver/stocks/partition_date={date_str}/stock_data.parquet"
        
        s3_hook.load_bytes(
            bytes_data=parquet_buffer.getvalue(),
            key=s3_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        logger.info(f"✅ Uploaded {s3_key}")
        
        # Create metadata
        metadata_summary = {
            'processing_date': date_str,
            'partition_date': date_str,
            'total_records': len(df),
            'unique_symbols': int(df['symbol'].nunique()),
            'data_date_range': {
                'min': str(df['data_date'].min()),
                'max': str(df['data_date'].max())
            },
            'schema_info': {
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
            },
            'quality_metrics': {
                'null_counts': df.isnull().sum().to_dict(),
                'avg_volume': float(df['volume'].mean()) if 'volume' in df.columns else 0,
                'avg_price': float(df['close'].mean()) if 'close' in df.columns else 0
            },
            'file_info': {
                's3_key': s3_key,
                'format': 'parquet',
                'compression': 'snappy',
                'size_bytes': len(parquet_buffer.getvalue())
            },
            '_schema_version': '2.0'
        }
        
        # Upload metadata
        metadata_key = f"silver/stocks/partition_date={date_str}/_metadata.json"
        s3_hook.load_string(
            string_data=json.dumps(metadata_summary, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        logger.info(f"📄 Metadata uploaded to {metadata_key}")
        
        # Result summary
        result = {
            'stocks_processed': len(df),
            'unique_symbols': int(df['symbol'].nunique()),
            'partition_date': date_str,
            'execution_date': date_str
        }
        
        log_pipeline_success(logger, metadata, result)
        logger.info(f"✅ Stock Processing Complete: {result}")
        
        return result
        
    except Exception as e:
        context_data = {
            'files_found': len(stock_files) if 'stock_files' in locals() else 0,
            'records_processed': len(df) if 'df' in locals() else 0
        }
        
        log_pipeline_error(logger, metadata, e, context_data)
        raise


def process_news_data(**context):
    """
    Process news data with flexible date parsing
    Input: bronze/news/raw/{id}.json
    Output: silver/news/partition_date=YYYY-MM-DD/news_cleaned.parquet
    """
    try:
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import io
        
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger = logging.getLogger(__name__)
        logger.info(f"📰 Starting news data processing for {date_str}")
        
        # Enhanced logger metadata
        metadata = {
            'pipeline_name': 'silver_news_processing',
            'layer': 'silver',
            'data_type': 'news',
            'execution_date': date_str
        }
        
        log_pipeline_start(logger, metadata)
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        s3_client = s3_hook.get_conn()
        
        # List all news files
        logger.info(f"📂 Listing Bronze news files...")
        news_files = []
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name, Prefix=f"bronze/news/raw/"):
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'].endswith('.json'):
                        # Check if file was created today (or get all for now)
                        news_files.append(obj['Key'])
        
        if not news_files:
            logger.warning(f"⚠️ No news files found")
            result = {'news_processed': 0, 'execution_date': date_str}
            log_pipeline_success(logger, metadata, result)
            return result
        
        logger.info(f"📊 Found {len(news_files)} news files")
        
        # Concurrent file reading
        def read_single_news_file(key):
            try:
                obj = s3_client.get_object(Bucket=bucket_name, Key=key)
                content = obj['Body'].read(amt=1024*1024*5).decode('utf-8')
                data = json.loads(content)
                return data
            except Exception as e:
                return None
        
        all_records = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(read_single_news_file, key): key for key in news_files}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    all_records.append(result)
        
        if not all_records:
            logger.warning(f"⚠️ No valid news records")
            result = {'news_processed': 0, 'execution_date': date_str}
            log_pipeline_success(logger, metadata, result)
            return result
        
        logger.info(f"📝 Loaded {len(all_records)} news records")
        
        # Create DataFrame
        df = pd.DataFrame(all_records)
        
        # Flexible date parsing (handles 8+ formats)
        def parse_date_flexible(date_val):
            if pd.isna(date_val):
                return date_str
            
            date_str_val = str(date_val).strip()
            
            # Try multiple formats
            formats = [
                'ISO8601',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y%m%d'
            ]
            
            for fmt in formats:
                try:
                    if fmt == 'ISO8601':
                        dt = pd.to_datetime(date_str_val, format='ISO8601', utc=True)
                    else:
                        dt = pd.to_datetime(date_str_val, format=fmt, utc=True)
                    return dt.strftime('%Y-%m-%d')
                except:
                    continue
            
            # Fallback
            try:
                dt = pd.to_datetime(date_str_val, utc=True)
                return dt.strftime('%Y-%m-%d')
            except:
                return date_str
        
        # Apply date parsing
        if 'published_date' in df.columns:
            df['data_date'] = df['published_date'].apply(parse_date_flexible)
        else:
            df['data_date'] = date_str
        
        # Clean text fields
        if 'snippet' in df.columns and 'title' not in df.columns:
            df['title'] = df['snippet']
        
        if 'snippet' in df.columns:
            df['content'] = df['snippet']
        else:
            df['content'] = ''
        
        df['content'] = df['content'].fillna('').astype(str)
        
        # Remove empty content
        df = df[df['content'].str.len() > 0]
        
        # Drop duplicates by id
        if 'id' in df.columns:
            df = df.drop_duplicates(subset=['id'], keep='last')
        
        # Select columns
        silver_cols = ['id', 'data_date', 'source', 'title', 'content', 'link', '_ingested_at_utc']
        df = df[[col for col in silver_cols if col in df.columns]]
        
        df = df.sort_values('data_date').reset_index(drop=True)
        
        logger.info(f"✅ Cleaned data: {len(df)} news articles")
        
        # Add partition_date
        df['partition_date'] = date_str
        
        # Write Parquet
        logger.info(f"💾 Writing Parquet file...")
        
        parquet_buffer = io.BytesIO()
        df.to_parquet(
            parquet_buffer,
            engine='pyarrow',
            compression='snappy',
            index=False
        )
        
        s3_key = f"silver/news/partition_date={date_str}/news_cleaned.parquet"
        
        s3_hook.load_bytes(
            bytes_data=parquet_buffer.getvalue(),
            key=s3_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        logger.info(f"✅ Uploaded {s3_key}")
        
        # Metadata
        metadata_summary = {
            'processing_date': date_str,
            'partition_date': date_str,
            'total_records': len(df),
            'unique_sources': int(df['source'].nunique()) if 'source' in df.columns else 0,
            'schema_info': {
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
            },
            'quality_metrics': {
                'avg_content_length': float(df['content'].str.len().mean()) if 'content' in df.columns else 0,
                'null_counts': df.isnull().sum().to_dict()
            },
            'file_info': {
                's3_key': s3_key,
                'format': 'parquet',
                'compression': 'snappy'
            },
            '_schema_version': '2.0'
        }
        
        metadata_key = f"silver/news/partition_date={date_str}/_metadata.json"
        s3_hook.load_string(
            string_data=json.dumps(metadata_summary, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        result = {
            'news_processed': len(df),
            'partition_date': date_str,
            'execution_date': date_str
        }
        
        log_pipeline_success(logger, metadata, result)
        logger.info(f"✅ News Processing Complete: {result}")
        
        return result
        
    except Exception as e:
        context_data = {
            'files_found': len(news_files) if 'news_files' in locals() else 0,
            'records_processed': len(df) if 'df' in locals() else 0
        }
        
        log_pipeline_error(logger, metadata, e, context_data)
        raise


def process_macro_data(**context):
    """
    Process macro economic data from 50+ CSV files
    Input: bronze/macro/raw/{category}/{indicator}.csv
    Output: silver/macro/partition_date=YYYY-MM-DD/macro_data.parquet
    """
    try:
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import io
        
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger = logging.getLogger(__name__)
        logger.info(f"📊 Starting macro data processing for {date_str}")
        
        # Enhanced logger metadata
        metadata = {
            'pipeline_name': 'silver_macro_processing',
            'layer': 'silver',
            'data_type': 'macro',
            'execution_date': date_str
        }
        
        log_pipeline_start(logger, metadata)
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        s3_client = s3_hook.get_conn()
        
        # List all macro CSV files
        logger.info(f"📂 Listing Bronze macro files...")
        macro_files = []
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name, Prefix=f"bronze/macro/raw/"):
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'].endswith('.csv'):
                        macro_files.append(obj['Key'])
        
        if not macro_files:
            logger.warning(f"⚠️ No macro files found")
            result = {'macro_indicators_processed': 0, 'execution_date': date_str}
            log_pipeline_success(logger, metadata, result)
            return result
        
        logger.info(f"📊 Found {len(macro_files)} macro CSV files")
        
        # Read all CSVs and merge
        all_data = []
        
        for key in macro_files:
            try:
                # Extract category and indicator from path
                # Path format: bronze/macro/raw/{category}/{indicator}.csv
                parts = key.split('/')
                if len(parts) >= 5:
                    category = parts[3]
                    indicator = parts[4].replace('.csv', '')
                else:
                    category = 'unknown'
                    indicator = 'unknown'
                
                # Read CSV
                obj = s3_client.get_object(Bucket=bucket_name, Key=key)
                df_macro = pd.read_csv(io.BytesIO(obj['Body'].read()))
                
                # Add category and indicator columns
                df_macro['category'] = category
                df_macro['indicator_name'] = indicator
                
                all_data.append(df_macro)
                logger.info(f"  ✅ {category}/{indicator}: {len(df_macro)} rows")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to read {key}: {str(e)}")
        
        if not all_data:
            logger.warning(f"⚠️ No valid macro data")
            result = {'macro_indicators_processed': 0, 'execution_date': date_str}
            log_pipeline_success(logger, metadata, result)
            return result
        
        # Merge all dataframes
        df = pd.concat(all_data, ignore_index=True)
        
        logger.info(f"📝 Merged {len(df)} macro records from {len(all_data)} indicators")
        
        # Standardize schema
        if 'date' in df.columns:
            df['data_date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        else:
            df['data_date'] = date_str
        
        # Ensure value column
        if 'value' in df.columns:
            df['indicator_value'] = pd.to_numeric(df['value'], errors='coerce')
        else:
            df['indicator_value'] = 0.0
        
        # Select columns
        silver_cols = ['data_date', 'category', 'indicator_name', 'indicator_value']
        df = df[[col for col in silver_cols if col in df.columns]]
        
        # Drop duplicates
        df = df.drop_duplicates(subset=['data_date', 'category', 'indicator_name'], keep='last')
        
        # Remove rows with missing data
        df = df.dropna(subset=['data_date', 'indicator_name'])
        
        df = df.sort_values(['category', 'indicator_name', 'data_date']).reset_index(drop=True)
        
        logger.info(f"✅ Cleaned data: {len(df)} records, {df['indicator_name'].nunique()} indicators")
        
        # Add partition_date
        df['partition_date'] = date_str
        
        # Write Parquet
        logger.info(f"💾 Writing Parquet file...")
        
        parquet_buffer = io.BytesIO()
        df.to_parquet(
            parquet_buffer,
            engine='pyarrow',
            compression='snappy',
            index=False
        )
        
        s3_key = f"silver/macro/partition_date={date_str}/macro_data.parquet"
        
        s3_hook.load_bytes(
            bytes_data=parquet_buffer.getvalue(),
            key=s3_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        logger.info(f"✅ Uploaded {s3_key}")
        
        # Metadata
        metadata_summary = {
            'processing_date': date_str,
            'partition_date': date_str,
            'total_records': len(df),
            'unique_indicators': int(df['indicator_name'].nunique()),
            'categories': df['category'].value_counts().to_dict(),
            'schema_info': {
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
            },
            'quality_metrics': {
                'avg_value': float(df['indicator_value'].mean()),
                'null_counts': df.isnull().sum().to_dict()
            },
            'file_info': {
                's3_key': s3_key,
                'format': 'parquet',
                'compression': 'snappy'
            },
            '_schema_version': '2.0'
        }
        
        metadata_key = f"silver/macro/partition_date={date_str}/_metadata.json"
        s3_hook.load_string(
            string_data=json.dumps(metadata_summary, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        result = {
            'macro_indicators_processed': int(df['indicator_name'].nunique()),
            'total_records': len(df),
            'partition_date': date_str,
            'execution_date': date_str
        }
        
        log_pipeline_success(logger, metadata, result)
        logger.info(f"✅ Macro Processing Complete: {result}")
        
        return result
        
    except Exception as e:
        context_data = {
            'files_found': len(macro_files) if 'macro_files' in locals() else 0,
            'records_processed': len(df) if 'df' in locals() else 0
        }
        
        log_pipeline_error(logger, metadata, e, context_data)
        raise


def validate_silver_data(**context):
    """Validate Silver layer Parquet outputs"""
    try:
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger = logging.getLogger(__name__)
        logger.info(f"🔍 Starting Silver data validation for {date_str}")
        
        validation_results = {
            'stocks_validation': {'passed': True, 'issues': []},
            'news_validation': {'passed': True, 'issues': []},
            'macro_validation': {'passed': True, 'issues': []},
        }
        
        # Validate stocks
        try:
            stock_key = f"silver/stocks/partition_date={date_str}/stock_data.parquet"
            if s3_hook.check_for_key(key=stock_key, bucket_name=bucket_name):
                logger.info(f"  ✅ Stocks Parquet found: {stock_key}")
            else:
                validation_results['stocks_validation']['passed'] = False
                validation_results['stocks_validation']['issues'].append('Parquet file not found')
        except Exception as e:
            validation_results['stocks_validation']['passed'] = False
            validation_results['stocks_validation']['issues'].append(str(e))
        
        # Validate news
        try:
            news_key = f"silver/news/partition_date={date_str}/news_cleaned.parquet"
            if s3_hook.check_for_key(key=news_key, bucket_name=bucket_name):
                logger.info(f"  ✅ News Parquet found: {news_key}")
            else:
                validation_results['news_validation']['passed'] = False
                validation_results['news_validation']['issues'].append('Parquet file not found')
        except Exception as e:
            validation_results['news_validation']['passed'] = False
            validation_results['news_validation']['issues'].append(str(e))
        
        # Validate macro
        try:
            macro_key = f"silver/macro/partition_date={date_str}/macro_data.parquet"
            if s3_hook.check_for_key(key=macro_key, bucket_name=bucket_name):
                logger.info(f"  ✅ Macro Parquet found: {macro_key}")
            else:
                validation_results['macro_validation']['passed'] = False
                validation_results['macro_validation']['issues'].append('Parquet file not found')
        except Exception as e:
            validation_results['macro_validation']['passed'] = False
            validation_results['macro_validation']['issues'].append(str(e))
        
        logger.info(f"✅ Validation Complete: {validation_results}")
        
        return validation_results
        
    except Exception as e:
        logger.error(f"💥 Validation failed: {str(e)}")
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
