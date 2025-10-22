""""""

Gold Layer Pipeline (Aligned with S3_LAKEHOUSE_COMPLETE_STRUCTURE.md)Gold Layer DAG - Analytics & ML Feature Engineering with Spark

========================================================================Creates business intelligence views and ML-ready datasets



This DAG creates analytics tables from Silver layer with 4-layer architecture:Author: Banking Portfolio Team

Version: 2.0 (Spark-enabled)

Layer 1 - ANALYTICS: Business intelligence tablesDate: October 2025

  - market_features: Technical indicators (MA, RSI, volatility)"""

  - sector_performance: Sector aggregations

  - news_summary: Daily news aggregationfrom datetime import datetime, timedelta

  - macro_indicators: Macro trends with moving averagesfrom airflow import DAG

from airflow.operators.python import PythonOperator

Layer 2 - SENTIMENT_ANALYSIS: Sentiment aggregationsfrom airflow.operators.bash import BashOperator

  - News sentiment by date/sourcefrom airflow.operators.dummy import DummyOperator

from airflow.providers.amazon.aws.hooks.s3 import S3Hook

Layer 3 - SERVING: Pre-aggregated cache for BI dashboardsfrom airflow.utils.trigger_rule import TriggerRule

  - market_dashboard, sentiment_features, macro_features, risk_metricsfrom airflow.utils.dates import days_ago

import logging

Layer 4 - METADATA: Pipeline lineage and quality trackingimport os

  - pipeline_runs: Execution tracking with lineageimport json

  - quality_metrics: Data quality per tableimport pandas as pd

import numpy as np

Schedule: Daily at 8 AM (weekdays), after Silver layer

Dependencies: pandas, pyarrow, numpy# Import custom utilities

"""import sys

sys.path.append('/opt/airflow/plugins')

from airflow import DAGsys.path.append('/opt/airflow/utils')

from airflow.operators.python import PythonOperator# Temporarily comment out Spark imports for testing

from datetime import datetime, timedelta# from spark_utils import get_spark_manager, get_financial_processor, with_spark_session

import logging

import json# Import enhanced logging

import osfrom enhanced_logger import get_enhanced_logger, log_pipeline_start, log_pipeline_success, log_pipeline_error

import pandas as pd

import numpy as np# Default args

import pyarrow as padefault_args = {

import pyarrow.parquet as pq    'owner': 'banking-portfolio',

import io    'depends_on_past': False,

from enhanced_logger import log_pipeline_start, log_pipeline_success, log_pipeline_error    'start_date': datetime(2025, 10, 16),

    'email_on_failure': False,

# Default arguments    'email_on_retry': False,

default_args = {    'retries': int(os.getenv('MAX_RETRY_ATTEMPTS', 2)),

    'owner': 'finance_portfolio',    'retry_delay': timedelta(minutes=5),

    'depends_on_past': False,    'execution_timeout': timedelta(hours=2),

    'start_date': datetime(2024, 1, 1),}

    'email_on_failure': True,

    'email_on_retry': False,# DAG definition

    'retries': 3,dag = DAG(

    'retry_delay': timedelta(minutes=5),    'gold_layer_pipeline',

    'execution_timeout': timedelta(hours=4),    default_args=default_args,

}    description='Gold Layer - Analytics & ML Feature Engineering with Spark',

    schedule_interval='0 8 * * 1-5',  # 8:00 AM weekdays (after Silver DAG)

# DAG definition    catchup=False,

dag = DAG(    max_active_runs=1,

    'gold_layer_pipeline',    max_active_tasks=8,

    default_args=default_args,    tags=['gold', 'analytics', 'spark', 'ml-features'],

    description='Gold layer analytics (4-layer architecture: analytics/sentiment/serving/metadata)',)

    schedule_interval='0 8 * * 1-5',  # 8 AM weekdays

    catchup=False,def create_analytics_tables(**context):

    tags=['gold', 'lakehouse', 'analytics'],    """Create business intelligence tables based on gold_layer_etl.py logic"""

    max_active_runs=1    # Initialize enhanced logger

)    logger = get_enhanced_logger("gold_analytics_creation", "INFO")

    

    # Start pipeline operation tracking

def create_market_features(**context):    metadata = log_pipeline_start(

    """        logger,

    Layer 1 - ANALYTICS: Create market_features table with technical indicators        pipeline_name="gold_analytics_creation",

    Input: silver/stocks/partition_date=*/stock_data.parquet        layer="gold",

    Output: gold/analytics/market_features/partition_date=YYYY-MM-DD/*.parquet        operation="create_business_intelligence",

    """        dag_run_id=context.get('dag_run').run_id,

    try:        task_id=context.get('task_instance').task_id

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook    )

            

        execution_date = context['execution_date']    try:

        date_str = execution_date.strftime('%Y-%m-%d')        execution_date = context['execution_date']

                date_str = execution_date.strftime('%Y-%m-%d')

        logger = logging.getLogger(__name__)        

        logger.info(f"📊 Creating market features for {date_str}")        logger.log_progress(metadata, f"Starting analytics tables creation for {date_str}")

                

        metadata = {        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

            'pipeline_name': 'gold_market_features',        import pandas as pd

            'layer': 'gold',        import json

            'data_type': 'analytics',        

            'execution_date': date_str        # Initialize S3

        }        s3_hook = S3Hook(aws_conn_id='aws_default')

                bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')

        log_pipeline_start(logger, metadata)        

                results = {

        # Initialize S3            'market_summary_created': False,

        s3_hook = S3Hook(aws_conn_id='aws_default')            'stock_features_created': False,

        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')            'news_sentiment_created': False,

                    'execution_date': date_str

        # Read Silver stocks data (last 30 days for MA calculation)        }

        logger.info(f"📂 Reading Silver stocks data...")        

                s3_paths = []

        # Get last 30 days of data for moving averages        processed_records = 0

        all_stocks = []        

        for i in range(30):        # 1. Create Market Summary from Silver stocks data

            past_date = (execution_date - timedelta(days=i)).strftime('%Y-%m-%d')        try:

            stock_key = f"silver/stocks/partition_date={past_date}/stock_data.parquet"            logger.log_progress(metadata, "Creating market summary from silver stocks data")

                        

            try:            # Read processed stock data from Silver layer - aligned with actual structure

                obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=stock_key)            stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str.replace('-', '')}.csv"

                df_day = pd.read_parquet(io.BytesIO(obj['Body'].read()))            

                all_stocks.append(df_day)            if not s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name):

            except:                # Try alternative date format

                continue                alt_stock_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"

                        if s3_hook.check_for_key(key=alt_stock_key, bucket_name=bucket_name):

        if not all_stocks:                    stock_file_key = alt_stock_key

            logger.warning(f"⚠️ No stock data found for MA calculation")                else:

            result = {'features_created': 0, 'execution_date': date_str}                    logger.log_progress(metadata, "No stock data found for market summary in either format")

            log_pipeline_success(logger, metadata, result)                    results['market_summary_created'] = False

            return result                

                    if results['market_summary_created'] != False:  # Only proceed if we found data

        df = pd.concat(all_stocks, ignore_index=True)                # Read silver stocks data

        df['data_date'] = pd.to_datetime(df['data_date'])                csv_content = s3_hook.read_key(key=stock_file_key, bucket_name=bucket_name)

        df = df.sort_values(['symbol', 'data_date'])                stocks_df = pd.read_csv(pd.StringIO(csv_content))

                        

        logger.info(f"📝 Loaded {len(df)} stock records for {df['symbol'].nunique()} symbols")                logger.log_progress(metadata, f"Processing {len(stocks_df)} stock records for market summary",

                                          stock_records=len(stocks_df))

        # Calculate technical indicators per symbol                

        logger.info(f"📈 Calculating technical indicators...")                # Create market summary aligned with Silver schema

                        market_summary = {

        features = []                    'date': date_str,

                            'total_stocks': len(stocks_df),

        for symbol in df['symbol'].unique():                    'avg_close_price': float(stocks_df['close'].mean()) if len(stocks_df) > 0 else 0,

            df_symbol = df[df['symbol'] == symbol].copy()                    'total_volume': int(stocks_df['volume'].sum()) if len(stocks_df) > 0 else 0,

            df_symbol = df_symbol.sort_values('data_date')                    'avg_daily_return': float(stocks_df['daily_return'].mean() if 'daily_return' in stocks_df.columns else 0),

                                'price_gainers': len(stocks_df[stocks_df['daily_return'] > 0]) if 'daily_return' in stocks_df.columns and len(stocks_df) > 0 else 0,

            # Only process if we have today's data                    'price_losers': len(stocks_df[stocks_df['daily_return'] < 0]) if 'daily_return' in stocks_df.columns and len(stocks_df) > 0 else 0,

            if date_str not in df_symbol['data_date'].astype(str).values:                    'market_breadth_pct': (len(stocks_df[stocks_df['daily_return'] > 0]) / len(stocks_df) * 100) if 'daily_return' in stocks_df.columns and len(stocks_df) > 0 else 0,

                continue                    'unique_symbols': int(stocks_df['symbol'].nunique()) if 'symbol' in stocks_df.columns else len(stocks_df),

                                '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'

            # Moving Averages                }

            df_symbol['MA_5'] = df_symbol['close'].rolling(window=5, min_periods=1).mean()                

            df_symbol['MA_10'] = df_symbol['close'].rolling(window=10, min_periods=1).mean()                # Save market summary to Gold analytics

            df_symbol['MA_20'] = df_symbol['close'].rolling(window=20, min_periods=1).mean()                market_summary_key = f"gold/analytics/market_summary/market_summary_{date_str.replace('-', '')}.json"

            df_symbol['MA_30'] = df_symbol['close'].rolling(window=30, min_periods=1).mean()                s3_hook.load_string(

                                string_data=json.dumps(market_summary, ensure_ascii=False, indent=2),

            # RSI (14-day)                    key=market_summary_key,

            delta = df_symbol['close'].diff()                    bucket_name=bucket_name,

            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()                    replace=True

            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()                )

            rs = gain / loss                

            df_symbol['RSI_14'] = 100 - (100 / (1 + rs))                results['market_summary_created'] = True

                            logging.info(f"✅ Market summary created with {market_summary['total_stocks']} stocks")

            # Volatility (7-day standard deviation)                

            df_symbol['volatility_7d'] = df_symbol['close'].rolling(window=7, min_periods=1).std()            else:

                            logging.warning(f"⚠️ No stock data found for market summary")

            # Get today's row                

            today_row = df_symbol[df_symbol['data_date'].astype(str) == date_str].iloc[-1]        except Exception as e:

                        logging.error(f"❌ Market summary creation failed: {str(e)}")

            feature_record = {        

                'symbol': symbol,        # 2. Create Stock Features for ML aligned with Silver schema

                'data_date': date_str,        try:

                'close': today_row['close'],            if results['market_summary_created']:

                'volume': today_row['volume'],                # Use existing stocks_df if market summary was created

                'MA_5': round(today_row['MA_5'], 2) if pd.notna(today_row['MA_5']) else None,                if 'stocks_df' in locals() and not stocks_df.empty:

                'MA_10': round(today_row['MA_10'], 2) if pd.notna(today_row['MA_10']) else None,                    # Create ML-ready features using actual Silver schema

                'MA_20': round(today_row['MA_20'], 2) if pd.notna(today_row['MA_20']) else None,                    ml_features = stocks_df.copy()

                'MA_30': round(today_row['MA_30'], 2) if pd.notna(today_row['MA_30']) else None,                    

                'RSI_14': round(today_row['RSI_14'], 2) if pd.notna(today_row['RSI_14']) else None,                    # Ensure we have the required columns from Silver

                'volatility_7d': round(today_row['volatility_7d'], 2) if pd.notna(today_row['volatility_7d']) else None,                    if 'symbol' in ml_features.columns:

                'price_change': today_row.get('price_change', 0),                        ml_features['ticker'] = ml_features['symbol']  # Standardize naming

                'price_change_pct': today_row.get('price_change_pct', 0)                    

            }                    # Price-based features using actual Silver columns

                                if all(col in ml_features.columns for col in ['close', 'open']):

            features.append(feature_record)                        ml_features['price_change_pct'] = (ml_features['close'] - ml_features['open']) / ml_features['open']

                            

        df_features = pd.DataFrame(features)                    if all(col in ml_features.columns for col in ['high', 'low']):

                                ml_features['daily_range_pct'] = (ml_features['high'] - ml_features['low']) / ml_features['low']

        logger.info(f"✅ Created features for {len(df_features)} symbols")                    

                            # Volume features

        # Add partition_date                    if 'volume' in ml_features.columns:

        df_features['partition_date'] = date_str                        ml_features['volume_log'] = np.log1p(ml_features['volume'])

                                ml_features['volume_scaled'] = (ml_features['volume'] - ml_features['volume'].mean()) / ml_features['volume'].std()

        # Write Parquet                    

        parquet_buffer = io.BytesIO()                    # Technical indicators from Silver (if available)

        df_features.to_parquet(                    tech_columns = ['MA_5', 'MA_20', 'RSI', 'MACD', 'BB_position']

            parquet_buffer,                    for col in tech_columns:

            engine='pyarrow',                        if col not in ml_features.columns:

            compression='snappy',                            ml_features[col] = 0  # Default values if not available

            index=False                    

        )                    # Banking sector classification

                            big4_banks = ['VCB', 'BID', 'CTG', 'AGR']

        s3_key = f"gold/analytics/market_features/partition_date={date_str}/market_features.parquet"                    tier1_banks = ['VPB', 'TCB', 'MBB', 'STB', 'HDB', 'ACB']

                            

        s3_hook.load_bytes(                    def classify_bank_tier(symbol):

            bytes_data=parquet_buffer.getvalue(),                        symbol = str(symbol).upper()

            key=s3_key,                        if symbol in big4_banks:

            bucket_name=bucket_name,                            return 'BIG_4'

            replace=True                        elif symbol in tier1_banks:

        )                            return 'TIER_1'

                                else:

        logger.info(f"✅ Uploaded {s3_key}")                            return 'TIER_2'

                            

        # Metadata                    symbol_col = 'symbol' if 'symbol' in ml_features.columns else 'ticker'

        metadata_summary = {                    ml_features['bank_tier'] = ml_features[symbol_col].apply(classify_bank_tier)

            'processing_date': date_str,                    

            'partition_date': date_str,                    # Select final ML feature columns

            'total_symbols': len(df_features),                    feature_columns = ['symbol', 'date', 'close', 'volume', 'bank_tier']

            'indicators_calculated': ['MA_5', 'MA_10', 'MA_20', 'MA_30', 'RSI_14', 'volatility_7d'],                    if 'daily_return' in ml_features.columns:

            'schema_info': {                        feature_columns.append('daily_return')

                'columns': list(df_features.columns),                    if 'price_change_pct' in ml_features.columns:

                'dtypes': {col: str(dtype) for col, dtype in df_features.dtypes.items()}                        feature_columns.append('price_change_pct')

            },                    if 'volume_log' in ml_features.columns:

            'file_info': {                        feature_columns.append('volume_log')

                's3_key': s3_key,                    

                'format': 'parquet',                    # Add technical indicators

                'compression': 'snappy'                    feature_columns.extend([col for col in tech_columns if col in ml_features.columns])

            },                    

            '_schema_version': '2.0'                    final_ml_features = ml_features[feature_columns].copy()

        }                    

                            # Save ML features to Gold serving

        metadata_key = f"gold/analytics/market_features/partition_date={date_str}/_metadata.json"                    ml_features_csv = final_ml_features.to_csv(index=False)

        s3_hook.load_string(                    ml_features_key = f"gold/serving/ml_features/ml_features_{date_str.replace('-', '')}.csv"

            string_data=json.dumps(metadata_summary, indent=2),                s3_hook.load_string(

            key=metadata_key,                    string_data=ml_features_csv,

            bucket_name=bucket_name,                    key=ml_features_key,

            replace=True                    bucket_name=bucket_name,

        )                    replace=True

                        )

        result = {                

            'features_created': len(df_features),                results['stock_features_created'] = True

            'partition_date': date_str,                logging.info(f"✅ ML features created for {len(stocks_df)} stocks")

            'execution_date': date_str                

        }        except Exception as e:

                    logging.error(f"❌ Stock features creation failed: {str(e)}")

        log_pipeline_success(logger, metadata, result)        

        logger.info(f"✅ Market Features Complete: {result}")        # 3. Create News Sentiment Analytics aligned with Silver schema

                try:

        return result            news_file_key = f"silver/news/processed/clean_news_{date_str.replace('-', '')}.csv"

                    

    except Exception as e:            # Try alternative date format

        context_data = {            if not s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name):

            'features_created': len(df_features) if 'df_features' in locals() else 0                alt_news_key = f"silver/news/processed/clean_news_{date_str}.csv"

        }                if s3_hook.check_for_key(key=alt_news_key, bucket_name=bucket_name):

                            news_file_key = alt_news_key

        log_pipeline_error(logger, metadata, e, context_data)            

        raise            if s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name):

                # Read silver news data

                csv_content = s3_hook.read_key(key=news_file_key, bucket_name=bucket_name)

def create_sentiment_analysis(**context):                news_df = pd.read_csv(pd.StringIO(csv_content))

    """                

    Layer 2 - SENTIMENT_ANALYSIS: Aggregate news sentiment by date/source                logging.info(f"📰 Processing {len(news_df)} news articles for sentiment analytics")

    Input: silver/news/partition_date=*/news_cleaned.parquet                

    Output: gold/sentiment_analysis/partition_date=YYYY-MM-DD/*.parquet                # Create sentiment analytics using actual Silver schema

    """                sentiment_analytics = {

    try:                    'date': date_str,

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook                    'total_articles': len(news_df),

                            'sentiment_distribution': {},

        execution_date = context['execution_date']                    'topic_distribution': {},

        date_str = execution_date.strftime('%Y-%m-%d')                    'avg_content_length': 0,

                            'banking_articles': 0,

        logger = logging.getLogger(__name__)                    'positive_sentiment_ratio': 0,

        logger.info(f"📰 Creating sentiment analysis for {date_str}")                    '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'

                        }

        metadata = {                

            'pipeline_name': 'gold_sentiment_analysis',                # Handle sentiment columns based on actual Silver output

            'layer': 'gold',                if 'sentiment_basic' in news_df.columns:

            'data_type': 'sentiment_analysis',                    sentiment_analytics['sentiment_distribution'] = news_df['sentiment_basic'].value_counts().to_dict()

            'execution_date': date_str                    positive_count = len(news_df[news_df['sentiment_basic'] == 'POSITIVE'])

        }                    sentiment_analytics['positive_sentiment_ratio'] = (positive_count / len(news_df) * 100) if len(news_df) > 0 else 0

                        elif 'sentiment_score' in news_df.columns:

        log_pipeline_start(logger, metadata)                    # Create basic sentiment from scores

                            news_df['sentiment_basic'] = news_df['sentiment_score'].apply(

        # Initialize S3                        lambda x: 'POSITIVE' if x > 0.1 else ('NEGATIVE' if x < -0.1 else 'NEUTRAL')

        s3_hook = S3Hook(aws_conn_id='aws_default')                    )

        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')                    sentiment_analytics['sentiment_distribution'] = news_df['sentiment_basic'].value_counts().to_dict()

                            positive_count = len(news_df[news_df['sentiment_basic'] == 'POSITIVE'])

        # Read Silver news data                    sentiment_analytics['positive_sentiment_ratio'] = (positive_count / len(news_df) * 100) if len(news_df) > 0 else 0

        news_key = f"silver/news/partition_date={date_str}/news_cleaned.parquet"                

                        # Handle topic/category columns

        try:                if 'topic_category' in news_df.columns:

            obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=news_key)                    sentiment_analytics['topic_distribution'] = news_df['topic_category'].value_counts().to_dict()

            df_news = pd.read_parquet(io.BytesIO(obj['Body'].read()))                    sentiment_analytics['banking_articles'] = len(news_df[news_df['topic_category'] == 'BANKING'])

        except:                elif 'category' in news_df.columns:

            logger.warning(f"⚠️ No news data found")                    sentiment_analytics['topic_distribution'] = news_df['category'].value_counts().to_dict()

            result = {'sentiment_records': 0, 'execution_date': date_str}                    sentiment_analytics['banking_articles'] = len(news_df[news_df['category'].str.contains('BANK', case=False, na=False)])

            log_pipeline_success(logger, metadata, result)                

            return result                # Handle content length

                        if 'content_length' in news_df.columns:

        logger.info(f"📝 Loaded {len(df_news)} news articles")                    sentiment_analytics['avg_content_length'] = float(news_df['content_length'].mean())

                        elif 'combined_text' in news_df.columns:

        # Simple sentiment scoring (in production, use Vietnamese sentiment model)                    news_df['content_length'] = news_df['combined_text'].str.len()

        def calculate_sentiment(text):                    sentiment_analytics['avg_content_length'] = float(news_df['content_length'].mean())

            """Simple sentiment scoring based on keywords"""                elif 'title' in news_df.columns:

            text_lower = str(text).lower()                    news_df['content_length'] = news_df['title'].str.len()

                                sentiment_analytics['avg_content_length'] = float(news_df['content_length'].mean())

            positive_words = ['tăng', 'tốt', 'khả quan', 'lợi nhuận', 'phát triển', 'tăng trưởng']                

            negative_words = ['giảm', 'xấu', 'suy thoái', 'lỗ', 'khó khăn', 'rủi ro']                # Save sentiment analytics with S3 logging

                            sentiment_key = f"gold/analytics/sentiment_analysis/news_sentiment_{date_str.replace('-', '')}.json"

            pos_count = sum(1 for word in positive_words if word in text_lower)                logger.log_s3_operation(metadata, "write", sentiment_key, "analytics_json")

            neg_count = sum(1 for word in negative_words if word in text_lower)                s3_hook.load_string(

                                string_data=json.dumps(sentiment_analytics, ensure_ascii=False, indent=2),

            if pos_count > neg_count:                    key=sentiment_key,

                return 1.0, 'positive'                    bucket_name=bucket_name,

            elif neg_count > pos_count:                    replace=True

                return -1.0, 'negative'                )

            else:                s3_paths.append(sentiment_key)

                return 0.0, 'neutral'                processed_records += len(news_df)

                        

        # Calculate sentiment for each article                results['news_sentiment_created'] = True

        df_news[['sentiment_score', 'sentiment_label']] = df_news['content'].apply(                logger.log_progress(metadata, f"News sentiment analytics created for {len(news_df)} articles",

            lambda x: pd.Series(calculate_sentiment(x))                                  articles_processed=len(news_df))

        )                

                    else:

        # Aggregate by date and source                logger.log_progress(metadata, "No news data found for sentiment analytics")

        sentiment_agg = df_news.groupby(['data_date', 'source']).agg({                

            'id': 'count',        except Exception as e:

            'sentiment_score': 'mean',            logger.log_progress(metadata, f"News sentiment analytics failed: {str(e)}")

            'sentiment_label': lambda x: x.value_counts().to_dict()        

        }).reset_index()        # Log file operations

                logger.log_file_operations(metadata, s3_paths=s3_paths)

        sentiment_agg.columns = ['data_date', 'source', 'article_count', 'avg_sentiment', 'sentiment_distribution']        

                # Quality metrics

        # Count sentiment labels        quality_metrics = {

        def count_sentiments(dist_dict):            'analytics_completion_rate': sum(results.values()) / len(results) * 100,

            return {            'market_summary_status': results['market_summary_created'],

                'positive': dist_dict.get('positive', 0),            'stock_features_status': results['stock_features_created'],

                'negative': dist_dict.get('negative', 0),            'news_sentiment_status': results['news_sentiment_created'],

                'neutral': dist_dict.get('neutral', 0)            'total_analytics_created': sum(results.values())

            }        }

                

        sentiment_agg['sentiment_counts'] = sentiment_agg['sentiment_distribution'].apply(count_sentiments)        # Log data quality

        sentiment_agg = sentiment_agg.drop('sentiment_distribution', axis=1)        logger.log_data_quality(

                    metadata,

        # Add partition_date            source_count=3,  # Three analytics types attempted

        sentiment_agg['partition_date'] = date_str            target_count=sum(results.values()),

                    error_count=3 - sum(results.values()),

        logger.info(f"✅ Created sentiment analysis for {len(sentiment_agg)} source-date combinations")            quality_metrics=quality_metrics

                )

        # Write Parquet        

        parquet_buffer = io.BytesIO()        # Create detailed analytics metadata using enhanced logger structure

        sentiment_agg.to_parquet(        detailed_metadata = {

            parquet_buffer,            'analytics_info': {

            engine='pyarrow',                'execution_date': date_str,

            compression='snappy',                'pipeline_version': '2.0_analytics',

            index=False                'layer': 'gold',

        )                'operation': 'create_business_intelligence',

                        'processing_timestamp': pd.Timestamp.utcnow().isoformat() + 'Z',

        s3_key = f"gold/sentiment_analysis/partition_date={date_str}/sentiment_aggregated.parquet"                'input_sources': ['silver/stocks/processed/', 'silver/news/processed/'],

                        'output_location': 'gold/analytics/'

        s3_hook.load_bytes(            },

            bytes_data=parquet_buffer.getvalue(),            'analytics_summary': {

            key=s3_key,                'total_analytics_created': sum(results.values()),

            bucket_name=bucket_name,                'market_summary_created': results['market_summary_created'],

            replace=True                'stock_features_created': results['stock_features_created'],

        )                'news_sentiment_created': results['news_sentiment_created'],

                        'total_records_processed': processed_records,

        logger.info(f"✅ Uploaded {s3_key}")                'analytics_types': ['market_summary', 'ml_features', 'sentiment_analysis']

                    },

        # Metadata            'business_intelligence': {

        metadata_summary = {                'completion_rate_percent': round(sum(results.values()) / len(results) * 100, 2),

            'processing_date': date_str,                'analytics_outputs': s3_paths,

            'partition_date': date_str,                'serving_layer_ready': all([results['market_summary_created'], results['stock_features_created']]),

            'total_records': len(sentiment_agg),                'decision_support_metrics': {

            'total_articles_processed': int(df_news['id'].nunique()),                    'market_insights_available': results['market_summary_created'],

            'avg_sentiment_overall': float(df_news['sentiment_score'].mean()),                    'ml_features_ready': results['stock_features_created'],

            'file_info': {                    'sentiment_insights_available': results['news_sentiment_created']

                's3_key': s3_key,                }

                'format': 'parquet',            },

                'compression': 'snappy'            'data_governance': {

            },                'data_lineage': 'silver/stocks/processed/ + silver/news/processed/ -> gold/analytics/',

            '_schema_version': '2.0'                'transformation_applied': ['aggregation', 'feature_engineering', 'sentiment_analysis', 'ml_preparation'],

        }                'quality_checks': {

                            'all_analytics_completed': all(results.values()),

        metadata_key = f"gold/sentiment_analysis/partition_date={date_str}/_metadata.json"                    'output_files_created': len(s3_paths) > 0,

        s3_hook.load_string(                    'serving_layer_preparation': results['market_summary_created'] and results['stock_features_created']

            string_data=json.dumps(metadata_summary, indent=2),                }

            key=metadata_key,            }

            bucket_name=bucket_name,        }

            replace=True        

        )        # Save detailed metadata

                metadata_key = f"gold/analytics/metadata/analytics_creation_metadata_{date_str}.json"

        result = {        logger.log_s3_operation(metadata, "write", metadata_key, "metadata")

            'sentiment_records': len(sentiment_agg),        s3_hook.load_string(

            'articles_processed': int(df_news['id'].nunique()),            string_data=json.dumps(detailed_metadata, ensure_ascii=False, indent=2),

            'partition_date': date_str,            key=metadata_key,

            'execution_date': date_str            bucket_name=bucket_name,

        }            replace=True

                )

        log_pipeline_success(logger, metadata, result)        s3_paths.append(metadata_key)

        logger.info(f"✅ Sentiment Analysis Complete: {result}")        

                # Finish pipeline operation

        return result        final_metadata = log_pipeline_success(logger, metadata, 3, sum(results.values()))

                

    except Exception as e:        logger.log_progress(metadata, "Analytics tables creation completed successfully", **results)

        context_data = {        return results

            'records_created': len(sentiment_agg) if 'sentiment_agg' in locals() else 0        

        }    except Exception as e:

                # Error logging with context

        log_pipeline_error(logger, metadata, e, context_data)        context_data = {

        raise            'analytics_attempted': list(results.keys()) if 'results' in locals() else [],

            'stage': 'analytics_creation'

        }

def create_serving_cache(**context):        log_pipeline_error(logger, metadata, e, context_data)

    """        raise

    Layer 3 - SERVING: Create pre-aggregated cache for BI dashboards

    Input: gold/analytics/*, gold/sentiment_analysis/*def create_ml_features(**context):

    Output: gold/serving/*/partition_date=YYYY-MM-DD/*.parquet    """Create ML-ready feature datasets based on gold_layer_etl.py logic"""

    """    # Initialize enhanced logger

    try:    logger = get_enhanced_logger("gold_ml_features", "INFO")

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook    

            # Start pipeline operation tracking

        execution_date = context['execution_date']    metadata = log_pipeline_start(

        date_str = execution_date.strftime('%Y-%m-%d')        logger,

                pipeline_name="gold_ml_features_creation",

        logger = logging.getLogger(__name__)        layer="gold",

        logger.info(f"🎯 Creating serving cache for {date_str}")        operation="create_ml_datasets",

                dag_run_id=context.get('dag_run').run_id,

        metadata = {        task_id=context.get('task_instance').task_id

            'pipeline_name': 'gold_serving_cache',    )

            'layer': 'gold',    

            'data_type': 'serving',    try:

            'execution_date': date_str        execution_date = context['execution_date']

        }        date_str = execution_date.strftime('%Y-%m-%d')

                

        log_pipeline_start(logger, metadata)        logger.log_progress(metadata, f"Starting ML features creation for {date_str}")

                

        # Initialize S3        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

        s3_hook = S3Hook(aws_conn_id='aws_default')        import pandas as pd

        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')        import json

                

        # Read market features        # Initialize S3

        try:        s3_hook = S3Hook(aws_conn_id='aws_default')

            market_key = f"gold/analytics/market_features/partition_date={date_str}/market_features.parquet"        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')

            obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=market_key)        

            df_market = pd.read_parquet(io.BytesIO(obj['Body'].read()))        s3_paths = []

        except:        

            df_market = pd.DataFrame()        try:

                    logger.log_progress(metadata, "Reading processed stock data from Silver layer")

        # Read sentiment analysis            

        try:            # Read processed stock data from Silver layer - aligned with actual structure

            sentiment_key = f"gold/sentiment_analysis/partition_date={date_str}/sentiment_aggregated.parquet"            stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str.replace('-', '')}.csv"

            obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=sentiment_key)            

            df_sentiment = pd.read_parquet(io.BytesIO(obj['Body'].read()))            if not s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name):

        except:                # Try alternative date format

            df_sentiment = pd.DataFrame()                alt_stock_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"

                        if s3_hook.check_for_key(key=alt_stock_key, bucket_name=bucket_name):

        # Create market dashboard (top movers, volume leaders)                    stock_file_key = alt_stock_key

        if not df_market.empty:                else:

            market_dashboard = pd.DataFrame({                    logger.log_progress(metadata, "No stock data found for ML features")

                'data_date': [date_str],                    result = {'ml_features_records': 0, 'execution_date': date_str}

                'total_symbols': [len(df_market)],                    log_pipeline_success(logger, metadata, 0, 0)

                'avg_rsi': [df_market['RSI_14'].mean()],                    return result

                'avg_volatility': [df_market['volatility_7d'].mean()],            

                'top_gainers': [df_market.nlargest(10, 'price_change_pct')['symbol'].tolist()],            # Read and process data

                'top_losers': [df_market.nsmallest(10, 'price_change_pct')['symbol'].tolist()],            csv_content = s3_hook.read_key(key=stock_file_key, bucket_name=bucket_name)

                'high_volume': [df_market.nlargest(10, 'volume')['symbol'].tolist()],            df = pd.read_csv(pd.StringIO(csv_content))

                'partition_date': [date_str]            

            })            logger.log_progress(metadata, f"Processing {len(df)} records for ML features",

                                          input_records=len(df))

            # Write market dashboard            

            parquet_buffer = io.BytesIO()            # Create ML features aligned with Silver schema

            market_dashboard.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)            ml_df = df.copy()

                        

            s3_key = f"gold/serving/market_dashboard/partition_date={date_str}/dashboard.parquet"            # Standardize column names

            s3_hook.load_bytes(bytes_data=parquet_buffer.getvalue(), key=s3_key, bucket_name=bucket_name, replace=True)            if 'symbol' in ml_df.columns and 'ticker' not in ml_df.columns:

                            ml_df['ticker'] = ml_df['symbol']

            logger.info(f"✅ Market dashboard created: {s3_key}")            

                    # Price-based features using available columns

        # Create sentiment features (for ML models)            if all(col in ml_df.columns for col in ['close', 'open']):

        if not df_sentiment.empty:                ml_df['price_to_open_ratio'] = ml_df['close'] / ml_df['open']

            sentiment_features = df_sentiment[['data_date', 'source', 'avg_sentiment', 'article_count']].copy()            

            sentiment_features['partition_date'] = date_str            if all(col in ml_df.columns for col in ['high', 'low']):

                            ml_df['high_low_spread'] = (ml_df['high'] - ml_df['low']) / ml_df['low']

            parquet_buffer = io.BytesIO()                ml_df['price_position'] = (ml_df['close'] - ml_df['low']) / (ml_df['high'] - ml_df['low'])

            sentiment_features.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)            

                        # Volume features

            s3_key = f"gold/serving/sentiment_features/partition_date={date_str}/features.parquet"            if 'volume' in ml_df.columns:

            s3_hook.load_bytes(bytes_data=parquet_buffer.getvalue(), key=s3_key, bucket_name=bucket_name, replace=True)                ml_df['volume_log'] = np.log1p(ml_df['volume'])  # Log transform

                            vol_mean = ml_df['volume'].mean()

            logger.info(f"✅ Sentiment features created: {s3_key}")                vol_std = ml_df['volume'].std()

                        if vol_std > 0:

        result = {                    ml_df['volume_scaled'] = (ml_df['volume'] - vol_mean) / vol_std

            'market_dashboard_created': not df_market.empty,                else:

            'sentiment_features_created': not df_sentiment.empty,                    ml_df['volume_scaled'] = 0

            'partition_date': date_str,            

            'execution_date': date_str            # Return-based features

        }            if 'daily_return' in ml_df.columns:

                        ml_df['return_squared'] = ml_df['daily_return'] ** 2

        log_pipeline_success(logger, metadata, result)                ml_df['return_positive'] = (ml_df['daily_return'] > 0).astype(int)

        logger.info(f"✅ Serving Cache Complete: {result}")                ml_df['return_abs'] = abs(ml_df['daily_return'])

                    else:

        return result                # Calculate daily return if not present

                        if all(col in ml_df.columns for col in ['close', 'open']):

    except Exception as e:                    ml_df['daily_return'] = (ml_df['close'] - ml_df['open']) / ml_df['open']

        context_data = {}                    ml_df['return_squared'] = ml_df['daily_return'] ** 2

        log_pipeline_error(logger, metadata, e, context_data)                    ml_df['return_positive'] = (ml_df['daily_return'] > 0).astype(int)

        raise                    ml_df['return_abs'] = abs(ml_df['daily_return'])

            

            # Banking sector encoding

def track_pipeline_metadata(**context):            big4_banks = ['VCB', 'BID', 'CTG', 'AGR']

    """            tier1_banks = ['VPB', 'TCB', 'MBB', 'STB', 'HDB', 'ACB', 'TPB', 'VIB']

    Layer 4 - METADATA: Track pipeline execution lineage and quality            

    Output: gold/metadata/pipeline_runs/partition_date=YYYY-MM-DD/*.parquet            def encode_bank_tier(ticker):

    """                ticker = str(ticker).upper()

    try:                if ticker in big4_banks:

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook                    return 1.0  # Highest tier

                        elif ticker in tier1_banks:

        execution_date = context['execution_date']                    return 0.7  # Medium tier

        date_str = execution_date.strftime('%Y-%m-%d')                else:

                            return 0.3  # Lower tier

        logger = logging.getLogger(__name__)            

        logger.info(f"📊 Tracking pipeline metadata for {date_str}")            ticker_col = 'ticker' if 'ticker' in ml_df.columns else 'symbol'

                    ml_df['bank_tier_score'] = ml_df[ticker_col].apply(encode_bank_tier)

        # Initialize S3            

        s3_hook = S3Hook(aws_conn_id='aws_default')            # Technical signal encoding (use defaults if not available)

        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')            if 'trend_signal' in ml_df.columns:

                        ml_df['is_bullish'] = (ml_df['trend_signal'] == 'BULLISH').astype(int)

        # Get task results from XCom                ml_df['is_bearish'] = (ml_df['trend_signal'] == 'BEARISH').astype(int)

        ti = context['task_instance']            else:

        market_result = ti.xcom_pull(task_ids='create_market_features')                ml_df['is_bullish'] = 0

        sentiment_result = ti.xcom_pull(task_ids='create_sentiment_analysis')                ml_df['is_bearish'] = 0

        serving_result = ti.xcom_pull(task_ids='create_serving_cache')            

                    if 'rsi_signal' in ml_df.columns:

        # Create pipeline run record                ml_df['rsi_overbought'] = (ml_df['rsi_signal'] == 'OVERBOUGHT').astype(int)

        pipeline_run = {                ml_df['rsi_oversold'] = (ml_df['rsi_signal'] == 'OVERSOLD').astype(int)

            'run_id': context['dag_run'].run_id,            else:

            'execution_date': date_str,                ml_df['rsi_overbought'] = 0

            'dag_id': 'gold_layer_pipeline',                ml_df['rsi_oversold'] = 0

            'pipeline_layers': {            

                'analytics': {            # Target variables for supervised learning

                    'market_features_created': market_result.get('features_created', 0) if market_result else 0            if 'daily_return' in ml_df.columns:

                },                ml_df['target_direction'] = ml_df['daily_return'].apply(

                'sentiment_analysis': {                    lambda x: 'UP' if x > 0.02 else ('DOWN' if x < -0.02 else 'FLAT')

                    'sentiment_records': sentiment_result.get('sentiment_records', 0) if sentiment_result else 0                )

                },                ml_df['target_volatility'] = ml_df['return_abs'] if 'return_abs' in ml_df.columns else abs(ml_df['daily_return'])

                'serving': {            else:

                    'market_dashboard': serving_result.get('market_dashboard_created', False) if serving_result else False,                ml_df['target_direction'] = 'FLAT'

                    'sentiment_features': serving_result.get('sentiment_features_created', False) if serving_result else False                ml_df['target_volatility'] = 0

                }            

            },            # Select ML-ready features (only include columns that exist)

            'source_layers': ['bronze', 'silver'],            base_columns = ['ticker', 'date', 'close', 'volume', 'daily_return']

            'transformations': ['technical_indicators', 'sentiment_analysis', 'pre_aggregation'],            feature_columns = [col for col in base_columns if col in ml_df.columns]

            'status': 'SUCCESS',            

            'partition_date': date_str            additional_features = [

        }                'price_to_open_ratio', 'high_low_spread', 'price_position',

                        'volume_log', 'volume_scaled', 'return_squared', 'return_positive',

        df_metadata = pd.DataFrame([pipeline_run])                'return_abs', 'bank_tier_score', 'is_bullish', 'is_bearish',

                        'rsi_overbought', 'rsi_oversold', 'target_direction', 'target_volatility'

        # Write metadata            ]

        parquet_buffer = io.BytesIO()            

        df_metadata.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)            for col in additional_features:

                        if col in ml_df.columns:

        s3_key = f"gold/metadata/pipeline_runs/partition_date={date_str}/run_metadata.parquet"                    feature_columns.append(col)

        s3_hook.load_bytes(bytes_data=parquet_buffer.getvalue(), key=s3_key, bucket_name=bucket_name, replace=True)            

                    # Filter columns that exist and create final ML features

        logger.info(f"✅ Pipeline metadata tracked: {s3_key}")            ml_features_df = ml_df[feature_columns].copy()

                    

        return {'metadata_tracked': True, 'execution_date': date_str}            # Add metadata

                    ml_features_df['_ml_features_version'] = '2.0'

    except Exception as e:            ml_features_df['_created_at_utc'] = pd.Timestamp.utcnow().isoformat() + 'Z'

        logger.error(f"💥 Metadata tracking failed: {str(e)}")            

        raise            # Save ML features with S3 logging

            ml_csv_content = ml_features_df.to_csv(index=False)

            ml_features_key = f"gold/serving/ml_features/ml_features_{date_str.replace('-', '')}.csv"

# Task definitions            

create_market_features_task = PythonOperator(            logger.log_s3_operation(metadata, "write", ml_features_key, "ml_features_csv")

    task_id='create_market_features',            s3_hook.load_string(

    python_callable=create_market_features,                string_data=ml_csv_content,

    dag=dag,                key=ml_features_key,

)                bucket_name=bucket_name,

                replace=True

create_sentiment_task = PythonOperator(            )

    task_id='create_sentiment_analysis',            s3_paths.append(ml_features_key)

    python_callable=create_sentiment_analysis,            

    dag=dag,            # Create feature statistics for monitoring

)            feature_stats = {

                'total_samples': len(ml_features_df),

create_serving_task = PythonOperator(                'feature_count': len(feature_columns),

    task_id='create_serving_cache',                'target_distribution': ml_features_df['target_direction'].value_counts().to_dict() if 'target_direction' in ml_features_df.columns else {},

    python_callable=create_serving_cache,                'avg_return': float(ml_features_df['daily_return'].mean()) if 'daily_return' in ml_features_df.columns else 0,

    dag=dag,                'return_volatility': float(ml_features_df['daily_return'].std()) if 'daily_return' in ml_features_df.columns else 0,

)                'bank_tier_distribution': ml_features_df['bank_tier_score'].value_counts().to_dict() if 'bank_tier_score' in ml_features_df.columns else {},

                'processing_date': date_str,

track_metadata_task = PythonOperator(                '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'

    task_id='track_pipeline_metadata',            }

    python_callable=track_pipeline_metadata,            

    dag=dag,            # Save feature statistics with S3 logging

)            stats_key = f"gold/serving/metadata/feature_stats_{date_str.replace('-', '')}.json"

            logger.log_s3_operation(metadata, "write", stats_key, "feature_stats")

# Task dependencies            s3_hook.load_string(

# Layer 1 & 2 run in parallel → Layer 3 → Layer 4                string_data=json.dumps(feature_stats, ensure_ascii=False, indent=2),

[create_market_features_task, create_sentiment_task] >> create_serving_task >> track_metadata_task                key=stats_key,

                bucket_name=bucket_name,
                replace=True
            )
            s3_paths.append(stats_key)
            
            # Create detailed metadata using enhanced logger structure
            detailed_metadata = {
                'ml_features_info': {
                    'execution_date': date_str,
                    'pipeline_version': '2.0_ml_features',
                    'layer': 'gold',
                    'operation': 'create_ml_datasets',
                    'processing_timestamp': pd.Timestamp.utcnow().isoformat() + 'Z',
                    'input_source': stock_file_key,
                    'output_location': 'gold/serving/ml_features/'
                },
                'feature_engineering_summary': {
                    'total_samples': len(ml_features_df),
                    'feature_count': len(feature_columns),
                    'features_created': feature_columns,
                    'target_variables': ['target_direction', 'target_volatility'],
                    'bank_tier_encoding': {
                        'big_4_banks': ['VCB', 'BID', 'CTG', 'AGR'],
                        'tier_1_banks': ['VPB', 'TCB', 'MBB', 'STB', 'HDB', 'ACB']
                    }
                },
                'ml_readiness_metrics': {
                    'target_distribution': feature_stats['target_distribution'],
                    'avg_daily_return': feature_stats['avg_return'],
                    'return_volatility': feature_stats['return_volatility'],
                    'bank_tier_distribution': feature_stats['bank_tier_distribution'],
                    'features_with_nulls': len([col for col in ml_features_df.columns if ml_features_df[col].isnull().any()]),
                    'ml_pipeline_ready': True
                },
                'output_files': {
                    'ml_features_file': ml_features_key,
                    'feature_stats_file': stats_key,
                    'output_size_mb': round(len(ml_csv_content) / 1024 / 1024, 2)
                },
                'data_governance': {
                    'data_lineage': f'{stock_file_key} -> {ml_features_key}',
                    'transformation_applied': ['feature_engineering', 'bank_tier_encoding', 'target_creation', 'ml_preparation'],
                    'quality_checks': {
                        'no_null_targets': ml_features_df['target_direction'].notna().all() if 'target_direction' in ml_features_df.columns else True,
                        'valid_features': len(feature_columns) > 0,
                        'consistent_records': len(ml_features_df) == len(df)
                    }
                }
            }
            
            # Save detailed metadata
            metadata_key = f"gold/serving/metadata/ml_features_metadata_{date_str}.json"
            logger.log_s3_operation(metadata, "write", metadata_key, "metadata")
            s3_hook.load_string(
                string_data=json.dumps(detailed_metadata, ensure_ascii=False, indent=2),
                key=metadata_key,
                bucket_name=bucket_name,
                replace=True
            )
            s3_paths.append(metadata_key)
            
            # Log file operations
            logger.log_file_operations(metadata, s3_paths=s3_paths)
            
            # Quality metrics
            quality_metrics = {
                'ml_feature_creation_success': True,
                'feature_engineering_completion': 100.0,
                'target_variable_creation': 'target_direction' in ml_features_df.columns,
                'bank_tier_encoding_applied': 'bank_tier_score' in ml_features_df.columns,
                'feature_count': len(feature_columns)
            }
            
            # Log data quality
            logger.log_data_quality(
                metadata,
                source_count=len(df),
                target_count=len(ml_features_df),
                error_count=0,
                quality_metrics=quality_metrics
            )
            
            # Finish pipeline operation
            final_metadata = log_pipeline_success(logger, metadata, len(df), len(ml_features_df))
            
            result = {
                'ml_features_records': detailed_metadata['feature_engineering_summary']['total_samples'],
                'feature_columns': detailed_metadata['feature_engineering_summary']['feature_count'],
                'target_up_count': detailed_metadata['ml_readiness_metrics']['target_distribution'].get('UP', 0),
                'target_down_count': detailed_metadata['ml_readiness_metrics']['target_distribution'].get('DOWN', 0),
                'execution_date': date_str
            }
            
            logger.log_progress(metadata, "✅ ML features created successfully", **result)
            return result
            
        except Exception as e:
            logger.log_progress(metadata, f"❌ ML features creation failed: {str(e)}")
            log_pipeline_error(logger, metadata, e, {'stage': 'ml_features_creation', 'input_file': stock_file_key if 'stock_file_key' in locals() else 'unknown'})
            result = {'ml_features_records': 0, 'execution_date': date_str}
            return result
            
    except Exception as e:
        # Error logging with context
        context_data = {'stage': 'initialization'}
        log_pipeline_error(logger, metadata, e, context_data)
        raise
        
    except Exception as e:
        logging.error(f"💥 ML feature creation failed: {str(e)}")
        raise

def create_integrated_views(**context):
    """Create integrated views combining stocks and news data based on gold_layer_etl.py logic"""
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logging.info(f"🔗 Creating integrated views for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import json
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        try:
            # Read stock data - aligned with actual Silver structure
            stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str.replace('-', '')}.csv"
            has_stocks = s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name)
            
            if not has_stocks:
                # Try alternative date format
                alt_stock_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
                has_stocks = s3_hook.check_for_key(key=alt_stock_key, bucket_name=bucket_name)
                if has_stocks:
                    stock_file_key = alt_stock_key
            
            # Read news data - aligned with actual Silver structure
            news_file_key = f"silver/news/processed/clean_news_{date_str.replace('-', '')}.csv"
            has_news = s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name)
            
            if not has_news:
                # Try alternative date format
                alt_news_key = f"silver/news/processed/clean_news_{date_str}.csv"
                has_news = s3_hook.check_for_key(key=alt_news_key, bucket_name=bucket_name)
                if has_news:
                    news_file_key = alt_news_key
            
            if not has_stocks:
                logging.warning(f"⚠️ No stock data found for integrated view")
                return {'integrated_records': 0, 'execution_date': date_str}
            
            # Load stock data
            csv_content = s3_hook.read_key(key=stock_file_key, bucket_name=bucket_name)
            stocks_df = pd.read_csv(pd.StringIO(csv_content))
            
            logging.info(f"📈 Loaded {len(stocks_df)} stock records")
            
            # Create integrated view
            integrated_df = stocks_df.copy()
            
            # Add news sentiment data if available
            if has_news:
                try:
                    news_csv_content = s3_hook.read_key(key=news_file_key, bucket_name=bucket_name)
                    news_df = pd.read_csv(pd.StringIO(news_csv_content))
                    
                    logging.info(f"📰 Loaded {len(news_df)} news articles")
                    
                    # Aggregate news sentiment by date - aligned with Silver schema
                    daily_sentiment = {
                        'total_articles': len(news_df),
                        'positive_articles': 0,
                        'negative_articles': 0,
                        'neutral_articles': 0,
                        'banking_articles': 0,
                        'avg_content_length': 0
                    }
                    
                    # Handle sentiment columns based on actual Silver schema
                    if 'sentiment_basic' in news_df.columns:
                        daily_sentiment['positive_articles'] = len(news_df[news_df['sentiment_basic'] == 'POSITIVE'])
                        daily_sentiment['negative_articles'] = len(news_df[news_df['sentiment_basic'] == 'NEGATIVE'])
                        daily_sentiment['neutral_articles'] = len(news_df[news_df['sentiment_basic'] == 'NEUTRAL'])
                    elif 'sentiment_score' in news_df.columns:
                        daily_sentiment['positive_articles'] = len(news_df[news_df['sentiment_score'] > 0.1])
                        daily_sentiment['negative_articles'] = len(news_df[news_df['sentiment_score'] < -0.1])
                        daily_sentiment['neutral_articles'] = len(news_df[(news_df['sentiment_score'] >= -0.1) & (news_df['sentiment_score'] <= 0.1)])
                    
                    # Handle topic/category columns
                    if 'topic_category' in news_df.columns:
                        daily_sentiment['banking_articles'] = len(news_df[news_df['topic_category'] == 'BANKING'])
                    elif 'category' in news_df.columns:
                        daily_sentiment['banking_articles'] = len(news_df[news_df['category'].str.contains('BANK', case=False, na=False)])
                    
                    # Handle content length
                    if 'content_length' in news_df.columns:
                        daily_sentiment['avg_content_length'] = float(news_df['content_length'].mean())
                    elif 'combined_text' in news_df.columns:
                        daily_sentiment['avg_content_length'] = float(news_df['combined_text'].str.len().mean())
                    elif 'title' in news_df.columns:
                        daily_sentiment['avg_content_length'] = float(news_df['title'].str.len().mean())
                    
                    # Calculate sentiment score
                    if daily_sentiment['total_articles'] > 0:
                        sentiment_score = (daily_sentiment['positive_articles'] - daily_sentiment['negative_articles']) / daily_sentiment['total_articles']
                    else:
                        sentiment_score = 0.0
                    
                    # Add news features to stock data
                    integrated_df['news_sentiment_score'] = sentiment_score
                    integrated_df['daily_news_count'] = daily_sentiment['total_articles']
                    integrated_df['positive_news_ratio'] = daily_sentiment['positive_articles'] / max(daily_sentiment['total_articles'], 1)
                    integrated_df['banking_news_count'] = daily_sentiment['banking_articles']
                    
                    logging.info(f"✅ Integrated with news sentiment: score={sentiment_score:.3f}")
                    
                except Exception as news_error:
                    logging.error(f"❌ News integration failed: {str(news_error)}")
                    # Continue without news data
                    integrated_df['news_sentiment_score'] = 0.0
                    integrated_df['daily_news_count'] = 0
                    integrated_df['positive_news_ratio'] = 0.5
                    integrated_df['banking_news_count'] = 0
            else:
                # Add default news features when no news data
                integrated_df['news_sentiment_score'] = 0.0
                integrated_df['daily_news_count'] = 0
                integrated_df['positive_news_ratio'] = 0.5  # Neutral
                integrated_df['banking_news_count'] = 0
                logging.info(f"⚠️ No news data - using default sentiment values")
            
            # Add market context features
            integrated_df['market_cap_estimate'] = integrated_df['close'] * integrated_df['volume'] / 1000  # Simplified market cap proxy
            integrated_df['relative_performance'] = integrated_df['daily_return'] - integrated_df['daily_return'].mean()
            integrated_df['volume_percentile'] = integrated_df['volume'].rank(pct=True)
            
            # Banking sector specific features
            big4_banks = ['VCB', 'BID', 'CTG', 'AGR']
            tier1_banks = ['VPB', 'TCB', 'MBB', 'STB', 'HDB', 'ACB', 'TPB', 'VIB']
            
            def get_bank_sector(ticker):
                if ticker in big4_banks:
                    return 'STATE_OWNED'
                elif ticker in tier1_banks:
                    return 'PRIVATE_LARGE'
                else:
                    return 'PRIVATE_SMALL'
            
            integrated_df['bank_sector'] = integrated_df['ticker'].apply(get_bank_sector)
            
            # Add integrated view metadata
            integrated_df['_integrated_view_version'] = '1.0'
            integrated_df['_created_at_utc'] = pd.Timestamp.utcnow().isoformat() + 'Z'
            integrated_df['_has_news_data'] = has_news
            
            # Save integrated view to Gold serving layer
            integrated_csv_content = integrated_df.to_csv(index=False)
            integrated_key = f"gold/serving/integrated_view/integrated_view_{date_str.replace('-', '')}.csv"
            
            s3_hook.load_string(
                string_data=integrated_csv_content,
                key=integrated_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Create integrated view summary
            integrated_summary = {
                'processing_date': date_str,
                'total_records': len(integrated_df),
                'unique_stocks': integrated_df['ticker'].nunique() if 'ticker' in integrated_df.columns else integrated_df['symbol'].nunique(),
                'has_news_data': has_news,
                'market_summary': {
                    'avg_return': float(integrated_df['daily_return'].mean()) if 'daily_return' in integrated_df.columns else 0,
                    'total_volume': int(integrated_df['volume'].sum()) if 'volume' in integrated_df.columns else 0,
                    'avg_sentiment_score': float(integrated_df['news_sentiment_score'].mean()) if 'news_sentiment_score' in integrated_df.columns else 0
                },
                'sector_distribution': integrated_df['bank_sector'].value_counts().to_dict() if 'bank_sector' in integrated_df.columns else {},
                '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
            }
            
            # Save integrated summary to Gold metadata
            summary_key = f"gold/metadata/integrated_summary/integrated_summary_{date_str.replace('-', '')}.json"
            s3_hook.load_string(
                string_data=json.dumps(integrated_summary, ensure_ascii=False, indent=2),
                key=summary_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            result = {
                'integrated_records': len(integrated_df),
                'has_news_data': has_news,
                'unique_stocks': integrated_df['ticker'].nunique() if 'ticker' in integrated_df.columns else integrated_df['symbol'].nunique(),
                'execution_date': date_str
            }
            
            logging.info(f"✅ Integrated views created successfully: {result}")
            return result
            
        except Exception as e:
            logging.error(f"❌ Integrated view creation failed: {str(e)}")
            return {'integrated_records': 0, 'execution_date': date_str}
        
    except Exception as e:
        logging.error(f"💥 Integrated view creation failed: {str(e)}")
        raise

def validate_gold_output(**context):
    """Validate gold layer outputs for quality and completeness"""
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logging.info(f"🔍 Validating gold layer outputs for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import json
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        validation_results = {
            'execution_date': date_str,
            'files_checked': [],
            'validation_status': 'PASS',
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            # Check analytics tables
            analytics_key = f"gold/analytics/market_summary_{date_str}.json"
            if s3_hook.check_for_key(key=analytics_key, bucket_name=bucket_name):
                try:
                    analytics_content = s3_hook.read_key(key=analytics_key, bucket_name=bucket_name)
                    analytics_data = json.loads(analytics_content)
                    
                    validation_results['files_checked'].append('market_summary')
                    
                    # Validate analytics structure
                    required_fields = ['processing_date', 'market_summary', 'sector_performance', 'ml_features_meta']
                    missing_fields = [field for field in required_fields if field not in analytics_data]
                    
                    if missing_fields:
                        validation_results['errors'].append(f"Analytics missing fields: {missing_fields}")
                        validation_results['validation_status'] = 'FAIL'
                    
                    # Check market summary values
                    market_summary = analytics_data.get('market_summary', {})
                    total_stocks = market_summary.get('total_stocks', 0)
                    
                    if total_stocks < 10:
                        validation_results['warnings'].append(f"Low stock count: {total_stocks}")
                    
                    validation_results['metrics']['total_stocks'] = total_stocks
                    validation_results['metrics']['avg_daily_return'] = market_summary.get('avg_daily_return', 0)
                    
                    logging.info(f"✅ Analytics validation passed: {total_stocks} stocks")
                    
                except Exception as e:
                    validation_results['errors'].append(f"Analytics validation error: {str(e)}")
                    validation_results['validation_status'] = 'FAIL'
            else:
                validation_results['errors'].append("Missing analytics file")
                validation_results['validation_status'] = 'FAIL'
            
            # Check ML features
            ml_features_key = f"gold/ml_features/banking_features_{date_str}.csv"
            if s3_hook.check_for_key(key=ml_features_key, bucket_name=bucket_name):
                try:
                    ml_csv_content = s3_hook.read_key(key=ml_features_key, bucket_name=bucket_name)
                    ml_df = pd.read_csv(pd.StringIO(ml_csv_content))
                    
                    validation_results['files_checked'].append('ml_features')
                    
                    # Validate ML features structure
                    required_ml_columns = ['ticker', 'date', 'close', 'volume', 'daily_return', 
                                         'rsi_14', 'ma_20', 'banking_tier_score', 'target_return_5d']
                    missing_ml_columns = [col for col in required_ml_columns if col not in ml_df.columns]
                    
                    if missing_ml_columns:
                        validation_results['errors'].append(f"ML features missing columns: {missing_ml_columns}")
                        validation_results['validation_status'] = 'FAIL'
                    
                    # Check for null values in critical columns
                    critical_columns = ['close', 'volume', 'daily_return']
                    for col in critical_columns:
                        if col in ml_df.columns:
                            null_count = ml_df[col].isna().sum()
                            if null_count > 0:
                                validation_results['warnings'].append(f"Null values in {col}: {null_count}")
                    
                    # Check data ranges
                    if 'rsi_14' in ml_df.columns:
                        rsi_out_of_range = ((ml_df['rsi_14'] < 0) | (ml_df['rsi_14'] > 100)).sum()
                        if rsi_out_of_range > 0:
                            validation_results['errors'].append(f"RSI out of range (0-100): {rsi_out_of_range} records")
                            validation_results['validation_status'] = 'FAIL'
                    
                    validation_results['metrics']['ml_features_count'] = len(ml_df)
                    validation_results['metrics']['unique_tickers'] = ml_df['ticker'].nunique()
                    
                    logging.info(f"✅ ML features validation passed: {len(ml_df)} records")
                    
                except Exception as e:
                    validation_results['errors'].append(f"ML features validation error: {str(e)}")
                    validation_results['validation_status'] = 'FAIL'
            else:
                validation_results['errors'].append("Missing ML features file")
                validation_results['validation_status'] = 'FAIL'
            
            # Check integrated view
            integrated_key = f"gold/serving/integrated_view_{date_str}.csv"
            if s3_hook.check_for_key(key=integrated_key, bucket_name=bucket_name):
                try:
                    integrated_csv_content = s3_hook.read_key(key=integrated_key, bucket_name=bucket_name)
                    integrated_df = pd.read_csv(pd.StringIO(integrated_csv_content))
                    
                    validation_results['files_checked'].append('integrated_view')
                    
                    # Validate integrated view
                    required_integrated_columns = ['ticker', 'close', 'volume', 'daily_return', 
                                                 'news_sentiment_score', 'daily_news_count', 'bank_sector']
                    missing_integrated_columns = [col for col in required_integrated_columns if col not in integrated_df.columns]
                    
                    if missing_integrated_columns:
                        validation_results['errors'].append(f"Integrated view missing columns: {missing_integrated_columns}")
                        validation_results['validation_status'] = 'FAIL'
                    
                    # Check sentiment score range
                    if 'news_sentiment_score' in integrated_df.columns:
                        sentiment_out_of_range = ((integrated_df['news_sentiment_score'] < -1) | 
                                                (integrated_df['news_sentiment_score'] > 1)).sum()
                        if sentiment_out_of_range > 0:
                            validation_results['warnings'].append(f"Sentiment score out of range (-1,1): {sentiment_out_of_range} records")
                    
                    validation_results['metrics']['integrated_records'] = len(integrated_df)
                    validation_results['metrics']['bank_sectors'] = integrated_df['bank_sector'].value_counts().to_dict()
                    
                    logging.info(f"✅ Integrated view validation passed: {len(integrated_df)} records")
                    
                except Exception as e:
                    validation_results['errors'].append(f"Integrated view validation error: {str(e)}")
                    validation_results['validation_status'] = 'FAIL'
            else:
                validation_results['warnings'].append("Missing integrated view file")
            
            # Cross-validation checks
            if 'ml_features_count' in validation_results['metrics'] and 'integrated_records' in validation_results['metrics']:
                ml_count = validation_results['metrics']['ml_features_count']
                integrated_count = validation_results['metrics']['integrated_records']
                
                if abs(ml_count - integrated_count) > 2:  # Allow small variance
                    validation_results['warnings'].append(f"Record count mismatch: ML={ml_count}, Integrated={integrated_count}")
            
            # Save validation results
            validation_results['_created_at_utc'] = pd.Timestamp.utcnow().isoformat() + 'Z'
            validation_key = f"gold/metadata/validation_results_{date_str}.json"
            
            s3_hook.load_string(
                string_data=json.dumps(validation_results, ensure_ascii=False, indent=2),
                key=validation_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Log validation summary
            status_emoji = "✅" if validation_results['validation_status'] == 'PASS' else "❌"
            logging.info(f"{status_emoji} Validation completed: {validation_results['validation_status']}")
            
            if validation_results['errors']:
                logging.error(f"❌ Validation errors: {validation_results['errors']}")
            
            if validation_results['warnings']:
                logging.warning(f"⚠️ Validation warnings: {validation_results['warnings']}")
            
            logging.info(f"📊 Validation metrics: {validation_results['metrics']}")
            
            return validation_results
            
        except Exception as validation_error:
            validation_results['errors'].append(f"Validation process error: {str(validation_error)}")
            validation_results['validation_status'] = 'FAIL'
            logging.error(f"❌ Validation process failed: {str(validation_error)}")
            return validation_results
        
    except Exception as e:
        logging.error(f"💥 Gold validation failed: {str(e)}")
        raise

# Task definitions
start_gold = DummyOperator(
    task_id='start_gold_pipeline',
    dag=dag,
)

create_analytics = PythonOperator(
    task_id='create_analytics_tables',
    python_callable=create_analytics_tables,
    dag=dag,
)

create_ml = PythonOperator(
    task_id='create_ml_features',
    python_callable=create_ml_features,
    dag=dag,
)

create_integrated = PythonOperator(
    task_id='create_integrated_views',
    python_callable=create_integrated_views,
    dag=dag,
)

validate_output = PythonOperator(
    task_id='validate_gold_output',
    python_callable=validate_gold_output,
    dag=dag,
)

health_check = BashOperator(
    task_id='gold_health_check',
    bash_command="""
    echo "🔍 Gold Layer Health Check"
    echo "Timestamp: $(date)"
    echo "Pipeline: Gold Layer Analytics & ML Features with Spark"
    echo "Status: Processing completed"
    echo "Memory usage: $(free -h | grep '^Mem' | awk '{print $3 "/" $2}')"
    """,
    dag=dag,
)

end_gold = DummyOperator(
    task_id='end_gold_pipeline',
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag,
)

# Task dependencies
start_gold >> [create_analytics, create_ml] >> create_integrated >> validate_output >> health_check >> end_gold

# Make DAG available
globals()['gold_layer_pipeline'] = dag
