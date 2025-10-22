"""
Spark Session Manager and Utilities for Airflow DAGs
Provides centralized Spark operations and session management with S3 integration

Author: Banking Portfolio Team
Version: 2.0
Date: October 2025
"""

import os
import logging
from datetime import datetime
from airflow.exceptions import AirflowException
import findspark

try:
    # Initialize Spark
    findspark.init()
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import *
    from pyspark.sql.types import *
    from pyspark.sql.window import Window
    from delta import configure_spark_with_delta_pip
    SPARK_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Spark not available: {e}")
    SPARK_AVAILABLE = False

class SparkManager:
    """Centralized Spark session manager with S3 integration"""
    
    def __init__(self, app_name="FinancePortfolio"):
        self.app_name = app_name
        self.spark = None
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'bankanalystportfolio')
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_DEFAULT_REGION', 'ap-southeast-1')
        
    def get_spark_session(self):
        """Get or create Spark session with optimized configurations"""
        if self.spark is None:
            try:
                if not SPARK_AVAILABLE:
                    raise AirflowException("Spark is not available. Check installation.")
                
                logging.info("🔧 Creating Spark session...")
                
                # Spark configuration builder
                builder = SparkSession.builder \
                    .appName(f"{self.app_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}") \
                    .config("spark.sql.adaptive.enabled", "true") \
                    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
                    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
                    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
                    .config("spark.sql.adaptive.localShuffleReader.enabled", "true") \
                    .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128MB") \
                    .config("spark.sql.sources.partitionOverwriteMode", "dynamic") \
                    .config("spark.sql.parquet.compression.codec", "snappy")
                
                # S3 Configuration
                if self.aws_access_key and self.aws_secret_key:
                    builder = builder \
                        .config("spark.hadoop.fs.s3a.access.key", self.aws_access_key) \
                        .config("spark.hadoop.fs.s3a.secret.key", self.aws_secret_key) \
                        .config("spark.hadoop.fs.s3a.endpoint", f"s3.{self.aws_region}.amazonaws.com") \
                        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
                        .config("spark.hadoop.fs.s3a.aws.credentials.provider", 
                               "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
                        .config("spark.hadoop.fs.s3a.path.style.access", "false") \
                        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
                        .config("spark.hadoop.fs.s3a.fast.upload", "true") \
                        .config("spark.hadoop.fs.s3a.multipart.size", "64MB") \
                        .config("spark.hadoop.fs.s3a.connection.maximum", "200")
                
                # Memory and performance optimization
                builder = builder \
                    .config("spark.driver.memory", "2g") \
                    .config("spark.driver.maxResultSize", "1g") \
                    .config("spark.executor.memory", "2g") \
                    .config("spark.executor.cores", "2") \
                    .config("spark.default.parallelism", "8") \
                    .config("spark.sql.shuffle.partitions", "8")
                
                # Configure Delta Lake support
                builder = configure_spark_with_delta_pip(builder)
                
                self.spark = builder.getOrCreate()
                
                # Set log level
                self.spark.sparkContext.setLogLevel("WARN")
                
                logging.info(f"✅ Spark session created: {self.spark.version}")
                logging.info(f"📊 Spark UI: {self.spark.sparkContext.uiWebUrl}")
                
            except Exception as e:
                logging.error(f"❌ Failed to create Spark session: {str(e)}")
                raise AirflowException(f"Spark session creation failed: {str(e)}")
        
        return self.spark
    
    def stop_spark_session(self):
        """Stop Spark session and clean up resources"""
        if self.spark:
            try:
                self.spark.stop()
                self.spark = None
                logging.info("✅ Spark session stopped")
            except Exception as e:
                logging.error(f"❌ Error stopping Spark session: {str(e)}")
    
    def read_from_s3(self, s3_path, format="json", **options):
        """Read data from S3 using Spark"""
        try:
            spark = self.get_spark_session()
            full_path = f"s3a://{self.bucket_name}/{s3_path}"
            
            logging.info(f"📖 Reading from S3: {full_path}")
            
            reader = spark.read.format(format)
            
            # Add options
            for key, value in options.items():
                reader = reader.option(key, value)
            
            df = reader.load(full_path)
            
            logging.info(f"✅ Successfully read {df.count()} rows from {s3_path}")
            return df
            
        except Exception as e:
            logging.error(f"❌ Failed to read from S3 {s3_path}: {str(e)}")
            raise AirflowException(f"S3 read failed: {str(e)}")
    
    def write_to_s3(self, df, s3_path, format="parquet", mode="overwrite", **options):
        """Write DataFrame to S3 using Spark"""
        try:
            full_path = f"s3a://{self.bucket_name}/{s3_path}"
            
            logging.info(f"📝 Writing to S3: {full_path}")
            logging.info(f"📊 DataFrame info: {df.count()} rows, {len(df.columns)} columns")
            
            writer = df.write.format(format).mode(mode)
            
            # Add options
            for key, value in options.items():
                writer = writer.option(key, value)
            
            writer.save(full_path)
            
            logging.info(f"✅ Successfully wrote to {s3_path}")
            
        except Exception as e:
            logging.error(f"❌ Failed to write to S3 {s3_path}: {str(e)}")
            raise AirflowException(f"S3 write failed: {str(e)}")
    
    def create_temp_view(self, df, view_name):
        """Create temporary view for SQL operations"""
        try:
            df.createOrReplaceTempView(view_name)
            logging.info(f"📋 Created temp view: {view_name}")
        except Exception as e:
            logging.error(f"❌ Failed to create temp view {view_name}: {str(e)}")
            raise
    
    def sql(self, query):
        """Execute SQL query"""
        try:
            spark = self.get_spark_session()
            result = spark.sql(query)
            logging.info(f"🔍 Executed SQL query")
            return result
        except Exception as e:
            logging.error(f"❌ SQL execution failed: {str(e)}")
            raise

class FinancialDataProcessor:
    """Spark-based financial data processing utilities"""
    
    def __init__(self, spark_manager):
        self.spark_manager = spark_manager
        self.spark = spark_manager.get_spark_session()
    
    def calculate_technical_indicators(self, df, symbol_col="ticker", date_col="date", 
                                     price_cols=["open", "high", "low", "close"], volume_col="volume"):
        """Calculate technical indicators using Spark"""
        try:
            logging.info("📈 Calculating technical indicators with Spark...")
            
            # Define window specifications
            window_spec = Window.partitionBy(symbol_col).orderBy(date_col)
            window_5 = window_spec.rowsBetween(-4, 0)
            window_20 = window_spec.rowsBetween(-19, 0)
            window_50 = window_spec.rowsBetween(-49, 0)
            
            # Calculate moving averages
            df = df.withColumn("ma_5", avg("close").over(window_5)) \
                   .withColumn("ma_20", avg("close").over(window_20)) \
                   .withColumn("ma_50", avg("close").over(window_50))
            
            # Calculate daily returns
            df = df.withColumn("prev_close", lag("close", 1).over(window_spec)) \
                   .withColumn("daily_return", 
                              when(col("prev_close").isNotNull(), 
                                   (col("close") - col("prev_close")) / col("prev_close"))
                              .otherwise(None))
            
            # Calculate price ranges
            df = df.withColumn("high_low_pct", (col("high") - col("low")) / col("low") * 100) \
                   .withColumn("close_open_pct", (col("close") - col("open")) / col("open") * 100)
            
            # Calculate volume indicators
            df = df.withColumn("volume_ma_20", avg(volume_col).over(window_20)) \
                   .withColumn("volume_ratio", 
                              when(col("volume_ma_20") > 0, col(volume_col) / col("volume_ma_20"))
                              .otherwise(None))
            
            # Calculate volatility (rolling standard deviation)
            df = df.withColumn("volatility_20d", 
                              stddev("daily_return").over(window_20))
            
            # RSI calculation (simplified)
            df = df.withColumn("price_change", col("close") - lag("close", 1).over(window_spec))
            df = df.withColumn("gain", when(col("price_change") > 0, col("price_change")).otherwise(0))
            df = df.withColumn("loss", when(col("price_change") < 0, -col("price_change")).otherwise(0))
            
            window_14 = window_spec.rowsBetween(-13, 0)
            df = df.withColumn("avg_gain", avg("gain").over(window_14)) \
                   .withColumn("avg_loss", avg("loss").over(window_14)) \
                   .withColumn("rs", col("avg_gain") / col("avg_loss")) \
                   .withColumn("rsi_14", 100 - (100 / (1 + col("rs"))))
            
            # Clean up intermediate columns
            df = df.drop("prev_close", "price_change", "gain", "loss", "avg_gain", "avg_loss", "rs")
            
            logging.info("✅ Technical indicators calculated successfully")
            return df
            
        except Exception as e:
            logging.error(f"❌ Technical indicators calculation failed: {str(e)}")
            raise AirflowException(f"Technical indicators failed: {str(e)}")
    
    def validate_stock_data(self, df):
        """Validate stock data quality using Spark"""
        try:
            logging.info("🔍 Validating stock data quality...")
            
            total_rows = df.count()
            
            # Check for null values
            null_counts = {}
            for col_name in df.columns:
                null_count = df.filter(col(col_name).isNull()).count()
                null_counts[col_name] = null_count
            
            # Check for invalid values
            invalid_prices = df.filter(
                (col("open") <= 0) | 
                (col("high") <= 0) | 
                (col("low") <= 0) | 
                (col("close") <= 0)
            ).count()
            
            invalid_volume = df.filter(col("volume") < 0).count()
            
            # Check for logical inconsistencies
            invalid_high_low = df.filter(col("high") < col("low")).count()
            
            quality_report = {
                "total_rows": total_rows,
                "null_counts": null_counts,
                "invalid_prices": invalid_prices,
                "invalid_volume": invalid_volume,
                "invalid_high_low": invalid_high_low,
                "quality_score": 0.0
            }
            
            # Calculate quality score
            total_issues = sum(null_counts.values()) + invalid_prices + invalid_volume + invalid_high_low
            quality_report["quality_score"] = max(0, (1 - total_issues / (total_rows * len(df.columns))) * 100)
            
            logging.info(f"📊 Data Quality Report: {quality_report}")
            return quality_report
            
        except Exception as e:
            logging.error(f"❌ Data validation failed: {str(e)}")
            raise AirflowException(f"Data validation failed: {str(e)}")
    
    def aggregate_market_summary(self, df):
        """Create market summary using Spark aggregations"""
        try:
            logging.info("📊 Creating market summary...")
            
            summary = df.groupBy("date").agg(
                avg("close").alias("avg_close"),
                expr("percentile_approx(close, 0.5)").alias("median_close"),
                sum("volume").alias("total_volume"),
                avg("daily_return").alias("avg_return"),
                avg("volatility_20d").alias("avg_volatility"),
                count("ticker").alias("num_stocks"),
                min("close").alias("min_close"),
                max("close").alias("max_close")
            )
            
            # Add market trend indicator
            summary = summary.withColumn("market_trend",
                when(col("avg_return") > 0.02, "BULLISH")
                .when(col("avg_return") < -0.02, "BEARISH")
                .otherwise("NEUTRAL")
            )
            
            logging.info("✅ Market summary created successfully")
            return summary
            
        except Exception as e:
            logging.error(f"❌ Market summary creation failed: {str(e)}")
            raise AirflowException(f"Market summary failed: {str(e)}")

# Utility functions for DAGs
def get_spark_manager(app_name="FinancePortfolio"):
    """Get SparkManager instance"""
    return SparkManager(app_name)

def get_financial_processor(spark_manager=None):
    """Get FinancialDataProcessor instance"""
    if spark_manager is None:
        spark_manager = get_spark_manager()
    return FinancialDataProcessor(spark_manager)

def with_spark_session(func):
    """Decorator to handle Spark session lifecycle"""
    def wrapper(*args, **kwargs):
        spark_manager = get_spark_manager()
        try:
            result = func(spark_manager, *args, **kwargs)
            return result
        finally:
            spark_manager.stop_spark_session()
    return wrapper

# Schema definitions for structured data
def get_stock_schema():
    """Get schema for stock data"""
    return StructType([
        StructField("ticker", StringType(), False),
        StructField("date", DateType(), False),
        StructField("open", DoubleType(), False),
        StructField("high", DoubleType(), False),
        StructField("low", DoubleType(), False),
        StructField("close", DoubleType(), False),
        StructField("volume", LongType(), False),
        StructField("_source", StringType(), True),
        StructField("_ingest_time_utc", StringType(), True),
        StructField("_execution_date", StringType(), True)
    ])

def get_news_schema():
    """Get schema for news data"""
    return StructType([
        StructField("id", StringType(), False),
        StructField("title", StringType(), False),
        StructField("content", StringType(), True),
        StructField("publish_date", StringType(), False),
        StructField("source", StringType(), False),
        StructField("category", StringType(), True),
        StructField("url", StringType(), True),
        StructField("_ingest_time_utc", StringType(), True),
        StructField("_execution_date", StringType(), True)
    ])