"""
Silver Layer Pipeline (Aligned with S3_LAKEHOUSE_COMPLETE_STRUCTURE.md)
=========================================================================

This DAG processes Bronze layer data and writes to Silver layer with:
- PySpark distributed processing for scalability
- Parquet format with Snappy compression
- Hive-style partitioning: partition_date=YYYY-MM-DD
- Optimized for large-scale data processing
- Schema validation and data quality checks

Schedule: Daily at 7 AM (weekdays), after Bronze layer
Dependencies: pyspark, pyarrow, boto3
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
import json
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, upper, to_date, round as spark_round, when, isnan, coalesce
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType

# Default arguments
default_args = {
    'owner': 'finance_portfolio',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 29),  # Current date to avoid future execution date issues
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
    schedule_interval=None,  # Triggered by master_pipeline only
    catchup=False,
    tags=['silver', 'lakehouse', 'parquet'],
    max_active_runs=1
)


def get_spark_session(app_name="SilverLayer"):
    """Create or get existing Spark session with S3 support"""
    return SparkSession.builder \
        .appName(app_name) \
        .master("local[2]") \
        .config("spark.executor.memory", "1g") \
        .config("spark.driver.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "50") \
        .config("spark.driver.maxResultSize", "512m") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain") \
        .getOrCreate()


def process_stock_data(**context):
    """
    Process stock data using PySpark for distributed processing
    Input: bronze/stocks/raw/{ticker}_{date}.json (flat structure)
    Output: silver/stocks/partition_date=YYYY-MM-DD/stock_data.parquet
    """
    spark = None
    try:
        # Use current date for real-time processing
        from datetime import datetime
        date_str = datetime.now().strftime('%Y-%m-%d')
        execution_date = context.get('execution_date', datetime.now())
        
        logger = logging.getLogger(__name__)
        logger.info(f"📈 Starting PySpark stock data processing for {date_str}")
        
        # Initialize Spark
        spark = get_spark_session("Silver-StockProcessing")
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Read JSON files directly from S3 with PySpark
        bronze_path = f"s3a://{bucket_name}/bronze/stocks/raw/*.json"
        logger.info(f"📂 Reading from: {bronze_path}")
        
        # Read JSON with multiLine option
        df_raw = spark.read.option("multiLine", "true").json(bronze_path)
        
        # Check if data exists
        if df_raw.count() == 0:
            logger.warning(f"⚠️ No stock files found for {date_str}")
            return {'stocks_processed': 0, 'execution_date': date_str}
        
        logger.info(f"📊 Loaded {df_raw.count()} stock files")
        
        # Explode nested data array
        from pyspark.sql.functions import explode
        df_exploded = df_raw.withColumn("stock_record", explode("data")) \
            .select(
                col("ticker"),
                col("_source"),
                col("_ingested_at_utc"),
                col("stock_record.*")
            )
        
        # Clean and standardize with PySpark
        logger.info(f"🧹 Cleaning and standardizing data with PySpark...")
        
        df_cleaned = df_exploded \
            .withColumnRenamed("ticker", "symbol") \
            .withColumn("symbol", upper(col("symbol"))) \
            .withColumn("data_date", to_date(col("time"))) \
            .withColumn("open", col("open").cast(DoubleType())) \
            .withColumn("high", col("high").cast(DoubleType())) \
            .withColumn("low", col("low").cast(DoubleType())) \
            .withColumn("close", col("close").cast(DoubleType())) \
            .withColumn("volume", coalesce(col("volume").cast(LongType()), lit(0)))
        
        # Calculate technical indicators
        df_cleaned = df_cleaned \
            .withColumn("price_change", col("close") - col("open")) \
            .withColumn("price_change_pct", 
                       spark_round(((col("close") - col("open")) / col("open") * 100), 4))
        
        # Drop duplicates (keep last by sorting)
        from pyspark.sql.window import Window
        from pyspark.sql.functions import row_number, desc
        
        window_spec = Window.partitionBy("symbol", "data_date").orderBy(desc("_ingested_at_utc"))
        df_deduped = df_cleaned \
            .withColumn("row_num", row_number().over(window_spec)) \
            .filter(col("row_num") == 1) \
            .drop("row_num")
        
        # Remove rows with missing critical data
        df_final = df_deduped \
            .filter(col("symbol").isNotNull()) \
            .filter(col("data_date").isNotNull()) \
            .filter(col("close").isNotNull())
        
        # Add partition_date column
        df_final = df_final.withColumn("partition_date", lit(date_str))
        
        # Select columns for Silver layer
        silver_cols = ['symbol', 'data_date', 'open', 'high', 'low', 'close', 'volume',
                       'price_change', 'price_change_pct', '_source', '_ingested_at_utc', 'partition_date']
        df_final = df_final.select(*[c for c in silver_cols if c in df_final.columns])
        
        # Get statistics before writing
        total_records = df_final.count()
        unique_symbols = df_final.select("symbol").distinct().count()
        
        logger.info(f"✅ Cleaned data: {total_records} records, {unique_symbols} unique symbols")
        
        # Write to S3 as Parquet with partitioning
        output_path = f"s3a://{bucket_name}/silver/stocks"
        logger.info(f"💾 Writing Parquet to: {output_path}")
        
        df_final.write \
            .mode("overwrite") \
            .partitionBy("partition_date") \
            .parquet(output_path, compression="snappy")
        
        logger.info(f"✅ Uploaded to {output_path}")
        
        # Create metadata (using collect for small aggregations)
        stats = df_final.agg({
            'volume': 'mean',
            'close': 'mean'
        }).collect()[0]
        
        metadata_summary = {
            'processing_date': date_str,
            'partition_date': date_str,
            'total_records': total_records,
            'unique_symbols': unique_symbols,
            'processing_engine': 'pyspark',
            'quality_metrics': {
                'avg_volume': float(stats['avg(volume)']) if stats['avg(volume)'] else 0,
                'avg_price': float(stats['avg(close)']) if stats['avg(close)'] else 0
            },
            'file_info': {
                's3_path': output_path,
                'format': 'parquet',
                'compression': 'snappy',
                'partitioning': 'partition_date'
            },
            '_schema_version': '2.0'
        }
        
        # Upload metadata using boto3
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        s3_hook = S3Hook(aws_conn_id='aws_default')
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
            'stocks_processed': total_records,
            'unique_symbols': unique_symbols,
            'partition_date': date_str,
            'execution_date': date_str
        }
        logger.info(f"✅ Stock Processing Complete: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in process_stock_data: {str(e)}")
        raise
    finally:
        if spark:
            spark.stop()


def process_news_data(**context):
    """
    Process news data using PySpark with flexible date parsing
    Input: bronze/news/raw/{id}.json
    Output: silver/news/partition_date=YYYY-MM-DD/news_cleaned.parquet
    """
    spark = None
    try:
        # Use current date for real-time processing
        from datetime import datetime
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        logger = logging.getLogger(__name__)
        logger.info(f"📰 Starting PySpark news data processing for {date_str}")
        
        # Initialize Spark
        spark = get_spark_session("Silver-NewsProcessing")
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Read JSON files directly from S3
        bronze_path = f"s3a://{bucket_name}/bronze/news/raw/*.json"
        logger.info(f"📂 Reading from: {bronze_path}")
        
        df_raw = spark.read.option("multiLine", "true").json(bronze_path)
        
        if df_raw.count() == 0:
            logger.warning(f"⚠️ No news files found")
            return {'news_processed': 0, 'execution_date': date_str}
        
        logger.info(f"📊 Loaded {df_raw.count()} news files")
        
        # Clean and standardize
        from pyspark.sql.functions import when, length, coalesce
        
        # Handle date parsing - use coalesce to try different date columns
        df_cleaned = df_raw \
            .withColumn("data_date", 
                       coalesce(to_date(col("published_date")), 
                               to_date(col("date")),
                               lit(date_str))) \
            .withColumn("title", 
                       coalesce(col("title"), col("snippet"), lit(""))) \
            .withColumn("content", 
                       coalesce(col("combined_text"), col("snippet"), lit(""))) \
            .filter(length(col("content")) > 0)
        
        # Drop duplicates by id if exists
        if "id" in df_cleaned.columns:
            from pyspark.sql.window import Window
            from pyspark.sql.functions import row_number
            window_spec = Window.partitionBy("id").orderBy(col("_ingested_at_utc").desc())
            df_cleaned = df_cleaned \
                .withColumn("row_num", row_number().over(window_spec)) \
                .filter(col("row_num") == 1) \
                .drop("row_num")
        
        # Add partition_date
        df_final = df_cleaned.withColumn("partition_date", lit(date_str))
        
        # Select columns
        silver_cols = ['id', 'data_date', 'source', 'title', 'content', 'link', 
                       '_ingested_at_utc', 'partition_date']
        df_final = df_final.select(*[c for c in silver_cols if c in df_final.columns])
        
        total_records = df_final.count()
        logger.info(f"✅ Cleaned data: {total_records} news articles")
        
        # Write to S3 as Parquet with partitioning
        output_path = f"s3a://{bucket_name}/silver/news"
        logger.info(f"💾 Writing Parquet to: {output_path}")
        
        df_final.write \
            .mode("overwrite") \
            .partitionBy("partition_date") \
            .parquet(output_path, compression="snappy")
        
        logger.info(f"✅ Uploaded to {output_path}")
        
        # Metadata
        unique_sources = df_final.select("source").distinct().count() if "source" in df_final.columns else 0
        
        metadata_summary = {
            'processing_date': date_str,
            'partition_date': date_str,
            'total_records': total_records,
            'unique_sources': unique_sources,
            'processing_engine': 'pyspark',
            'file_info': {
                's3_path': output_path,
                'format': 'parquet',
                'compression': 'snappy',
                'partitioning': 'partition_date'
            },
            '_schema_version': '2.0'
        }
        
        # Upload metadata
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        s3_hook = S3Hook(aws_conn_id='aws_default')
        metadata_key = f"silver/news/partition_date={date_str}/_metadata.json"
        s3_hook.load_string(
            string_data=json.dumps(metadata_summary, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        result = {
            'news_processed': total_records,
            'partition_date': date_str,
            'execution_date': date_str
        }
        logger.info(f"✅ News Processing Complete: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in process_news_data: {str(e)}")
        raise
    finally:
        if spark:
            spark.stop()


def process_macro_data(**context):
    """
    Process macro economic data from 50+ CSV files using PySpark
    Input: bronze/macro/raw/{category}/{indicator}.csv
    Output: silver/macro/partition_date=YYYY-MM-DD/macro_data.parquet
    """
    spark = None
    try:
        # Use current date for real-time processing
        from datetime import datetime
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        logger = logging.getLogger(__name__)
        logger.info(f"📊 Starting PySpark macro data processing for {date_str}")
        
        # Initialize Spark
        spark = get_spark_session("Silver-MacroProcessing")
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Read all CSV files from S3 with PySpark
        bronze_path = f"s3a://{bucket_name}/bronze/macro/raw/*/*.csv"
        logger.info(f"📂 Reading from: {bronze_path}")
        
        # Read CSV files with header
        df_raw = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv(bronze_path)
        
        if df_raw.count() == 0:
            logger.warning(f"⚠️ No macro files found")
            return {'macro_indicators_processed': 0, 'execution_date': date_str}
        
        logger.info(f"📊 Loaded macro CSV files")
        
        # Extract category and indicator from file path using input_file_name()
        from pyspark.sql.functions import input_file_name, split, element_at
        
        df_with_meta = df_raw \
            .withColumn("file_path", input_file_name()) \
            .withColumn("path_parts", split(col("file_path"), "/")) \
            .withColumn("category", element_at(col("path_parts"), -2)) \
            .withColumn("indicator_name", 
                       split(element_at(col("path_parts"), -1), "\\.").getItem(0))
        
        # Standardize schema
        df_cleaned = df_with_meta \
            .withColumn("data_date", 
                       coalesce(to_date(col("date")), lit(date_str))) \
            .withColumn("indicator_value", 
                       coalesce(col("value").cast(DoubleType()), lit(0.0)))
        
        # Select columns
        silver_cols = ['data_date', 'category', 'indicator_name', 'indicator_value']
        df_final = df_cleaned.select(*silver_cols)
        
        # Drop duplicates
        df_final = df_final.dropDuplicates(['data_date', 'category', 'indicator_name'])
        
        # Remove rows with missing data
        df_final = df_final \
            .filter(col("data_date").isNotNull()) \
            .filter(col("indicator_name").isNotNull())
        
        # Add partition_date
        df_final = df_final.withColumn("partition_date", lit(date_str))
        
        total_records = df_final.count()
        unique_indicators = df_final.select("indicator_name").distinct().count()
        
        logger.info(f"✅ Cleaned data: {total_records} records, {unique_indicators} indicators")
        
        # Write to S3 as Parquet with partitioning
        output_path = f"s3a://{bucket_name}/silver/macro"
        logger.info(f"💾 Writing Parquet to: {output_path}")
        
        df_final.write \
            .mode("overwrite") \
            .partitionBy("partition_date") \
            .parquet(output_path, compression="snappy")
        
        logger.info(f"✅ Uploaded to {output_path}")
        
        # Metadata
        metadata_summary = {
            'processing_date': date_str,
            'partition_date': date_str,
            'total_records': total_records,
            'unique_indicators': unique_indicators,
            'processing_engine': 'pyspark',
            'file_info': {
                's3_path': output_path,
                'format': 'parquet',
                'compression': 'snappy',
                'partitioning': 'partition_date'
            },
            '_schema_version': '2.0'
        }
        
        # Upload metadata
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        s3_hook = S3Hook(aws_conn_id='aws_default')
        metadata_key = f"silver/macro/partition_date={date_str}/_metadata.json"
        s3_hook.load_string(
            string_data=json.dumps(metadata_summary, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        result = {
            'macro_indicators_processed': unique_indicators,
            'total_records': total_records,
            'partition_date': date_str,
            'execution_date': date_str
        }
        logger.info(f"✅ Macro Processing Complete: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in process_macro_data: {str(e)}")
        raise
    finally:
        if spark:
            spark.stop()


def validate_silver_data(**context):
    """Validate Silver layer Parquet outputs"""
    try:
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Use current date for real-time processing
        from datetime import datetime
        date_str = datetime.now().strftime('%Y-%m-%d')
        execution_date = context.get('execution_date', datetime.now())
        
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
