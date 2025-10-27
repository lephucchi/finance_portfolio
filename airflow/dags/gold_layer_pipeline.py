# Gold Layer Pipeline - 4-Layer Analytics Architecture
# =====================================================
# Creates analytics-ready datasets with technical indicators, sentiment analysis,
# serving cache, and pipeline metadata tracking.
#
# 4-Layer Architecture (aligned with S3_LAKEHOUSE_COMPLETE_STRUCTURE.md):
# 1. analytics/ - Business intelligence tables (Athena queryable)
#    - market_features: Technical indicators (MA, RSI, volatility) 
#    - sector_performance: Sector aggregations
#    - news_summary: Daily news aggregation
#    - macro_indicators: Macro trends with moving averages
#
# 2. sentiment_analysis/ - Specialized sentiment (Athena queryable)
#    - News sentiment aggregated by date/source
#
# 3. serving/ - Pre-aggregated cache for BI (S3 direct read)
#    - market_dashboard, sentiment_features, macro_features, risk_metrics
#
# 4. metadata/ - Pipeline lineage and quality tracking (NOT in Athena)
#    - pipeline_runs: Execution tracking with lineage
#    - quality_metrics: Data quality per table
#
# Author: finance_portfolio
# Schedule: Daily at 8 AM (weekdays), after Silver layer
# Dependencies: pandas, pyarrow, numpy
# =====================================================

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import numpy as np
from io import BytesIO
import json
import logging
import sys

# sys.path.append('/opt/airflow/dags')
# Removed enhanced_logger import for simplified testing

# Configuration
S3_BUCKET = 'bankanalystportfolio'
S3_CONN_ID = 'aws_s3_conn'

# Default arguments
default_args = {
    'owner': 'finance_portfolio',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 27),  # Current date to avoid future execution date issues
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=4),
}

# DAG definition
dag = DAG(
    'gold_layer_pipeline',
    default_args=default_args,
    description='Gold layer - 4-layer analytics architecture',
    schedule_interval=None,  # Triggered by master_pipeline only
    catchup=False,
    tags=['gold', 'lakehouse', 'analytics'],
    max_active_runs=1
)

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for stock data"""
    df = df.sort_values('data_date')
    
    # Moving Averages
    df['MA_5'] = df['close'].rolling(window=5).mean()
    df['MA_10'] = df['close'].rolling(window=10).mean()
    df['MA_20'] = df['close'].rolling(window=20).mean()
    df['MA_30'] = df['close'].rolling(window=30).mean()
    
    # RSI (14-day)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # Volatility (7-day)
    df['volatility_7d'] = df['close'].rolling(window=7).std()
    
    return df

def create_market_features(**context):
    """
    Layer 1 - ANALYTICS: Create market_features table with technical indicators
    Input: silver/stocks/partition_date=*/stock_data.parquet
    Output: gold/analytics/market_features/partition_date=YYYY-MM-DD/*.parquet
    """
    execution_date = context['execution_date']
    # Simple logging instead of enhanced logger calls
    logging.info(f"🚀 Starting gold_layer create_market_features operation")
    
    try:
        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
        end_date = execution_date.date()
        start_date = end_date - timedelta(days=30)  # 30 days for MA calculation
        
        logging.info(f"Processing stocks from {start_date} to {end_date}")
        
        # List all stock files in Silver layer
        silver_prefix = 'silver/stocks/'
        all_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=silver_prefix)
        
        if not all_files:
            logging.warning("No Silver stock files found")
            return
        
        # Filter parquet files in date range
        stock_files = [f for f in all_files if f.endswith('.parquet') and 'partition_date=' in f]
        all_stocks = []
        
        # Read stock files
        for file_key in stock_files:
            try:
                # Extract partition date
                partition_str = file_key.split('partition_date=')[1].split('/')[0]
                partition_date = datetime.strptime(partition_str, '%Y-%m-%d').date()
                
                if start_date <= partition_date <= end_date:
                    obj = s3_hook.get_key(file_key, bucket_name=S3_BUCKET)
                    parquet_data = obj.get()['Body'].read()
                    df = pd.read_parquet(BytesIO(parquet_data))
                    all_stocks.append(df)
            except Exception as e:
                logging.error(f"Error reading {file_key}: {e}")
                continue
        
        if not all_stocks:
            logging.warning("No stock data in date range")
            return
        
        # Combine all stocks
        stocks_df = pd.concat(all_stocks, ignore_index=True)
        
        # Calculate technical indicators by symbol
        results = []
        for symbol in stocks_df['symbol'].unique():
            symbol_df = stocks_df[stocks_df['symbol'] == symbol].copy()
            symbol_df = calculate_technical_indicators(symbol_df)
            results.append(symbol_df)
        
        market_features_df = pd.concat(results, ignore_index=True)
        
        # Write to Gold analytics layer with partitioning
        partition_date_str = end_date.strftime('%Y-%m-%d')
        gold_prefix = f'gold/analytics/market_features/partition_date={partition_date_str}/'
        
        # Save as Parquet
        parquet_buffer = BytesIO()
        market_features_df.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
        parquet_buffer.seek(0)
        
        s3_key = f'{gold_prefix}market_features_{end_date.strftime("%Y%m%d")}.parquet'
        s3_hook.load_bytes(
            parquet_buffer.read(),
            key=s3_key,
            bucket_name=S3_BUCKET,
            replace=True
        )
        
        # Save metadata
        metadata = {
            'execution_date': execution_date.isoformat(),
            'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'records_processed': len(market_features_df),
            'symbols_count': market_features_df['symbol'].nunique(),
            'features': ['MA_5', 'MA_10', 'MA_20', 'MA_30', 'RSI_14', 'volatility_7d']
        }
        
        metadata_key = f'{gold_prefix}_metadata.json'
        s3_hook.load_string(
            json.dumps(metadata, indent=2),
            key=metadata_key,
            bucket_name=S3_BUCKET,
            replace=True
        )
        
        logging.info("✅ Operation completed successfully")
        logging.info(f"✅ Market features completed successfully: {len(market_features_df)} records, {market_features_df['symbol'].nunique()} symbols")
        
    except Exception as e:
        logging.error(f"❌ Error in create_market_features: {str(e)}")
        raise

def create_sector_performance(**context):
    """
    Layer 1 - ANALYTICS: Create sector_performance table
    Input: gold/analytics/market_features/partition_date=*/
    Output: gold/analytics/sector_performance/partition_date=YYYY-MM-DD/*.parquet
    """
    execution_date = context['execution_date']
    logging.info("🚀 Starting operation")
    
    try:
        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
        end_date = execution_date.date()
        partition_date_str = end_date.strftime('%Y-%m-%d')
        
        # Read market features
        market_prefix = f'gold/analytics/market_features/partition_date={partition_date_str}/'
        market_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=market_prefix)
        market_parquet = [f for f in market_files if f.endswith('.parquet')]
        
        if not market_parquet:
            logging.warning("No market features found")
            return
        
        obj = s3_hook.get_key(market_parquet[0], bucket_name=S3_BUCKET)
        market_df = pd.read_parquet(BytesIO(obj.get()['Body'].read()))
        
        # Define sector mapping (simplified)
        sector_mapping = {
            'VCB': 'Banking', 'BID': 'Banking', 'CTG': 'Banking', 'ACB': 'Banking',
            'VNM': 'Consumer', 'MSN': 'Consumer', 'MWG': 'Consumer',
            'HPG': 'Materials', 'HSG': 'Materials',
            'VIC': 'Real Estate', 'VHM': 'Real Estate'
        }
        
        market_df['sector'] = market_df['symbol'].map(sector_mapping).fillna('Others')
        
        # Calculate sector aggregations
        sector_agg = market_df.groupby('sector').agg({
            'price_change_pct': 'mean',
            'volatility_7d': 'mean',
            'volume': 'mean'
        }).reset_index()
        
        sector_agg.columns = ['sector', 'avg_price_change_pct', 'avg_volatility', 'avg_volume']
        sector_agg['data_date'] = end_date
        
        # Write to Gold analytics layer
        gold_prefix = f'gold/analytics/sector_performance/partition_date={partition_date_str}/'
        
        parquet_buffer = BytesIO()
        sector_agg.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
        parquet_buffer.seek(0)
        
        s3_key = f'{gold_prefix}sector_performance_{end_date.strftime("%Y%m%d")}.parquet'
        s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)
        
        logging.info("✅ Operation completed successfully")
        logging.info(f"Sector performance created: {len(sector_agg)} sectors")
        
    except Exception as e:
        logging.error("❌ Operation failed")
        raise

def create_news_summary(**context):
    """
    Layer 1 - ANALYTICS: Create news_summary table  
    Input: silver/news/partition_date=*/news_cleaned.parquet
    Output: gold/analytics/news_summary/partition_date=YYYY-MM-DD/*.parquet
    """
    execution_date = context['execution_date']
    logging.info("🚀 Starting operation")
    
    try:
        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
        end_date = execution_date.date()
        partition_date_str = end_date.strftime('%Y-%m-%d')
        
        # Read news data
        news_prefix = f'silver/news/partition_date={partition_date_str}/'
        news_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=news_prefix)
        news_parquet = [f for f in news_files if f.endswith('.parquet')]
        
        if not news_parquet:
            logging.warning("No news data found")
            return
        
        obj = s3_hook.get_key(news_parquet[0], bucket_name=S3_BUCKET)
        news_df = pd.read_parquet(BytesIO(obj.get()['Body'].read()))
        
        # Create news summary
        news_summary = {
            'data_date': end_date,
            'total_articles': len(news_df),
            'unique_sources': news_df['source'].nunique() if 'source' in news_df.columns else 1,
            'avg_sentiment': float(news_df['sentiment_score'].mean()) if 'sentiment_score' in news_df.columns else 0.0,
            'articles_positive': len(news_df[news_df['sentiment_score'] > 0]) if 'sentiment_score' in news_df.columns else 0,
            'articles_negative': len(news_df[news_df['sentiment_score'] < 0]) if 'sentiment_score' in news_df.columns else 0,
            'avg_title_length': float(news_df['title'].str.len().mean()) if 'title' in news_df.columns else 0,
            'top_source': news_df['source'].value_counts().index[0] if 'source' in news_df.columns and not news_df.empty else 'unknown'
        }
        
        summary_df = pd.DataFrame([news_summary])
        
        # Write to Gold analytics layer
        gold_prefix = f'gold/analytics/news_summary/partition_date={partition_date_str}/'
        
        parquet_buffer = BytesIO()
        summary_df.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
        parquet_buffer.seek(0)
        
        s3_key = f'{gold_prefix}news_summary_{end_date.strftime("%Y%m%d")}.parquet'
        s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)
        
        logging.info("✅ Operation completed successfully")
        logging.info(f"News summary created: {news_summary['total_articles']} articles")
        
    except Exception as e:
        logging.error("❌ Operation failed")
        raise

def create_macro_indicators(**context):
    """
    Layer 1 - ANALYTICS: Create macro_indicators table with trends
    Input: silver/macro/partition_date=*/macro_data.parquet
    Output: gold/analytics/macro_indicators/partition_date=YYYY-MM-DD/*.parquet
    """
    execution_date = context['execution_date']
    logging.info("🚀 Starting operation")
    
    try:
        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
        end_date = execution_date.date()
        start_date = end_date - timedelta(days=30)  # 30 days for MA calculation
        
        # Read macro data from multiple days
        all_macro = []
        for i in range(30):
            date_check = end_date - timedelta(days=i)
            partition_date_str = date_check.strftime('%Y-%m-%d')
            
            macro_prefix = f'silver/macro/partition_date={partition_date_str}/'
            macro_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=macro_prefix)
            macro_parquet = [f for f in macro_files if f.endswith('.parquet')]
            
            if macro_parquet:
                try:
                    obj = s3_hook.get_key(macro_parquet[0], bucket_name=S3_BUCKET)
                    macro_df = pd.read_parquet(BytesIO(obj.get()['Body'].read()))
                    all_macro.append(macro_df)
                except:
                    continue
        
        if not all_macro:
            logging.warning("No macro data found")
            return
        
        combined_macro = pd.concat(all_macro, ignore_index=True)
        
        # Calculate indicators with moving averages
        indicators_df = []
        for indicator in combined_macro['indicator_name'].unique():
            indicator_data = combined_macro[combined_macro['indicator_name'] == indicator].copy()
            indicator_data = indicator_data.sort_values('data_date')
            
            # Calculate moving averages
            indicator_data['MA_7'] = indicator_data['indicator_value'].rolling(window=7).mean()
            indicator_data['MA_30'] = indicator_data['indicator_value'].rolling(window=30).mean()
            
            # Calculate changes
            indicator_data['value_change'] = indicator_data['indicator_value'].diff()
            indicator_data['value_change_pct'] = indicator_data['indicator_value'].pct_change() * 100
            
            # Keep only today's data with historical calculations
            today_data = indicator_data[indicator_data['data_date'].astype(str) == end_date.strftime('%Y-%m-%d')]
            if not today_data.empty:
                indicators_df.append(today_data)
        
        if indicators_df:
            final_indicators = pd.concat(indicators_df, ignore_index=True)
            
            # Write to Gold analytics layer
            partition_date_str = end_date.strftime('%Y-%m-%d')
            gold_prefix = f'gold/analytics/macro_indicators/partition_date={partition_date_str}/'
            
            parquet_buffer = BytesIO()
            final_indicators.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
            parquet_buffer.seek(0)
            
            s3_key = f'{gold_prefix}macro_indicators_{end_date.strftime("%Y%m%d")}.parquet'
            s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)
            
            logging.info("✅ Operation completed successfully")
            logging.info(f"Macro indicators created: {len(final_indicators)} indicators")
        
    except Exception as e:
        logging.error("❌ Operation failed")
        raise

def create_sentiment_analysis(**context):
    """
    Layer 2 - SENTIMENT_ANALYSIS: Aggregate news sentiment by date and source
    Input: silver/news/partition_date=*/news_cleaned.parquet
    Output: gold/sentiment_analysis/partition_date=YYYY-MM-DD/*.parquet
    """
    execution_date = context['execution_date']
    logging.info("🚀 Starting operation")
    
    try:
        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
        end_date = execution_date.date()
        start_date = end_date - timedelta(days=7)  # Last 7 days
        
        # Read news data from multiple days
        all_news = []
        for i in range(7):
            date_check = end_date - timedelta(days=i)
            partition_date_str = date_check.strftime('%Y-%m-%d')
            
            news_prefix = f'silver/news/partition_date={partition_date_str}/'
            news_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=news_prefix)
            news_parquet = [f for f in news_files if f.endswith('.parquet')]
            
            if news_parquet:
                try:
                    obj = s3_hook.get_key(news_parquet[0], bucket_name=S3_BUCKET)
                    news_df = pd.read_parquet(BytesIO(obj.get()['Body'].read()))
                    all_news.append(news_df)
                except:
                    continue
        
        if not all_news:
            logging.warning("No news data found")
            return
        
        combined_news = pd.concat(all_news, ignore_index=True)
        
        # Ensure we have necessary columns
        if 'data_date' not in combined_news.columns:
            combined_news['data_date'] = end_date
        if 'source' not in combined_news.columns:
            combined_news['source'] = 'unknown'
        if 'sentiment_score' not in combined_news.columns:
            combined_news['sentiment_score'] = 0.0
        
        # Aggregate sentiment by date and source
        sentiment_agg = combined_news.groupby(['data_date', 'source']).agg({
            'sentiment_score': ['mean', 'count'],
        }).reset_index()
        
        sentiment_agg.columns = ['data_date', 'source', 'avg_sentiment', 'article_count']
        
        # Calculate sentiment counts
        sentiment_agg['positive_count'] = combined_news.groupby(['data_date', 'source'])['sentiment_score'].apply(lambda x: (x > 0).sum()).values
        sentiment_agg['negative_count'] = combined_news.groupby(['data_date', 'source'])['sentiment_score'].apply(lambda x: (x < 0).sum()).values
        sentiment_agg['neutral_count'] = sentiment_agg['article_count'] - sentiment_agg['positive_count'] - sentiment_agg['negative_count']
        
        # Calculate sentiment change (compared to previous day)
        sentiment_agg = sentiment_agg.sort_values(['source', 'data_date'])
        sentiment_agg['sentiment_change_pct'] = sentiment_agg.groupby('source')['avg_sentiment'].pct_change() * 100
        
        # Write to Gold sentiment_analysis layer
        partition_date_str = end_date.strftime('%Y-%m-%d')
        gold_prefix = f'gold/sentiment_analysis/partition_date={partition_date_str}/'
        
        parquet_buffer = BytesIO()
        sentiment_agg.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
        parquet_buffer.seek(0)
        
        s3_key = f'{gold_prefix}sentiment_analysis_{end_date.strftime("%Y%m%d")}.parquet'
        s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)
        
        logging.info("✅ Operation completed successfully")
        logging.info(f"Sentiment analysis created: {len(sentiment_agg)} aggregations")
        
    except Exception as e:
        logging.error("❌ Operation failed")
        raise

def create_serving_cache(**context):
    """
    Layer 3 - SERVING: Create pre-aggregated cache for BI dashboards
    Input: gold/analytics/*, gold/sentiment_analysis/*
    Output: gold/serving/*/partition_date=YYYY-MM-DD/*.parquet
    """
    execution_date = context['execution_date']
    logging.info("🚀 Starting operation")
    
    try:
        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
        end_date = execution_date.date()
        partition_date_str = end_date.strftime('%Y-%m-%d')
        
        # 1. Market Dashboard Cache
        market_prefix = f'gold/analytics/market_features/partition_date={partition_date_str}/'
        market_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=market_prefix)
        market_parquet = [f for f in market_files if f.endswith('.parquet')]
        
        if market_parquet:
            obj = s3_hook.get_key(market_parquet[0], bucket_name=S3_BUCKET)
            market_df = pd.read_parquet(BytesIO(obj.get()['Body'].read()))
            
            # Create market dashboard cache (subset of columns for fast loading)
            dashboard_df = market_df[['symbol', 'data_date', 'open', 'close', 'volume', 'MA_20', 'RSI_14', 'volatility_7d', 'price_change_pct']].copy()
            
            # Write market dashboard
            serving_prefix = f'gold/serving/market_dashboard/partition_date={partition_date_str}/'
            
            parquet_buffer = BytesIO()
            dashboard_df.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
            parquet_buffer.seek(0)
            
            s3_key = f'{serving_prefix}market_dashboard_{end_date.strftime("%Y%m%d")}.parquet'
            s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)
            logging.info("Market dashboard cache created")
        
        # 2. Sentiment Features Cache
        sentiment_prefix = f'gold/sentiment_analysis/partition_date={partition_date_str}/'
        sentiment_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=sentiment_prefix)
        sentiment_parquet = [f for f in sentiment_files if f.endswith('.parquet')]
        
        if sentiment_parquet:
            obj = s3_hook.get_key(sentiment_parquet[0], bucket_name=S3_BUCKET)
            sentiment_df = pd.read_parquet(BytesIO(obj.get()['Body'].read()))
            
            # Create sentiment features cache
            sentiment_df['positive_pct'] = (sentiment_df['positive_count'] / sentiment_df['article_count'] * 100).round(2)
            sentiment_df['negative_pct'] = (sentiment_df['negative_count'] / sentiment_df['article_count'] * 100).round(2)
            
            features_df = sentiment_df[['data_date', 'source', 'article_count', 'avg_sentiment', 'positive_pct', 'negative_pct']].copy()
            
            # Write sentiment features
            serving_prefix = f'gold/serving/sentiment_features/partition_date={partition_date_str}/'
            
            parquet_buffer = BytesIO()
            features_df.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
            parquet_buffer.seek(0)
            
            s3_key = f'{serving_prefix}sentiment_features_{end_date.strftime("%Y%m%d")}.parquet'
            s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)
            logging.info("Sentiment features cache created")
        
        # 3. Risk Metrics Cache (from market features)
        if market_parquet:
            risk_df = market_df[['data_date', 'symbol', 'volatility_7d']].copy()
            
            # Write risk metrics
            serving_prefix = f'gold/serving/risk_metrics/partition_date={partition_date_str}/'
            
            parquet_buffer = BytesIO()
            risk_df.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
            parquet_buffer.seek(0)
            
            s3_key = f'{serving_prefix}risk_metrics_{end_date.strftime("%Y%m%d")}.parquet'
            s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)
            logging.info("Risk metrics cache created")
        
        logging.info("✅ Operation completed successfully")
        logging.info("Serving cache creation completed")
        
    except Exception as e:
        logging.error("❌ Operation failed")
        raise

def track_pipeline_metadata(**context):
    """
    Layer 4 - METADATA: Track pipeline execution metadata and lineage
    Output: gold/metadata/pipeline_runs/partition_date=YYYY-MM-DD/*.json
    """
    execution_date = context['execution_date']
    logging.info("🚀 Starting operation")
    
    try:
        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
        end_date = execution_date.date()
        
        # Create pipeline run metadata
        pipeline_metadata = {
            'pipeline_run_id': f"gold_transform_{end_date.strftime('%Y-%m-%d')}_{int(execution_date.timestamp())}",
            'run_id': context['dag_run'].run_id,
            'execution_date': execution_date.isoformat(),
            'dag_id': 'gold_layer_pipeline',
            'start_time': datetime.now().isoformat(),
            'source_layers': ['silver/stocks', 'silver/news', 'silver/macro'],
            'transformations': [
                'calculate_technical_indicators',
                'aggregate_sentiment',
                'create_serving_cache'
            ],
            'gold_outputs': {
                'analytics/market_features': f'partition_date={end_date.strftime("%Y-%m-%d")}',
                'analytics/sector_performance': f'partition_date={end_date.strftime("%Y-%m-%d")}',
                'analytics/news_summary': f'partition_date={end_date.strftime("%Y-%m-%d")}',
                'analytics/macro_indicators': f'partition_date={end_date.strftime("%Y-%m-%d")}',
                'sentiment_analysis': f'partition_date={end_date.strftime("%Y-%m-%d")}',
                'serving/market_dashboard': f'partition_date={end_date.strftime("%Y-%m-%d")}',
                'serving/sentiment_features': f'partition_date={end_date.strftime("%Y-%m-%d")}',
                'serving/risk_metrics': f'partition_date={end_date.strftime("%Y-%m-%d")}'
            },
            'version': 'v2.0-option2'
        }
        
        # Write metadata
        partition_date_str = end_date.strftime('%Y-%m-%d')
        metadata_prefix = f'gold/metadata/pipeline_runs/partition_date={partition_date_str}/'
        metadata_key = f'{metadata_prefix}run_{context["dag_run"].run_id}.json'
        
        s3_hook.load_string(
            json.dumps(pipeline_metadata, indent=2),
            key=metadata_key,
            bucket_name=S3_BUCKET,
            replace=True
        )
        
        logging.info("✅ Operation completed successfully")
        logging.info(f"Pipeline metadata tracked: {metadata_key}")
        
    except Exception as e:
        logging.error("❌ Operation failed")
        raise

# Define tasks
task_market_features = PythonOperator(
    task_id='create_market_features',
    python_callable=create_market_features,
    dag=dag
)

task_sector_performance = PythonOperator(
    task_id='create_sector_performance',
    python_callable=create_sector_performance,
    dag=dag
)

task_news_summary = PythonOperator(
    task_id='create_news_summary',
    python_callable=create_news_summary,
    dag=dag
)

task_macro_indicators = PythonOperator(
    task_id='create_macro_indicators',
    python_callable=create_macro_indicators,
    dag=dag
)

task_sentiment_analysis = PythonOperator(
    task_id='create_sentiment_analysis',
    python_callable=create_sentiment_analysis,
    dag=dag
)

task_serving_cache = PythonOperator(
    task_id='create_serving_cache',
    python_callable=create_serving_cache,
    dag=dag
)

task_pipeline_metadata = PythonOperator(
    task_id='track_pipeline_metadata',
    python_callable=track_pipeline_metadata,
    dag=dag
)

# Task dependencies aligned with 4-layer architecture
# Layer 1: Analytics tables (can run in parallel)
[task_market_features, task_news_summary, task_macro_indicators] >> task_sector_performance

# Layer 2: Sentiment analysis (independent)
task_sentiment_analysis

# Layer 3: Serving cache (depends on Layer 1 & 2)
[task_sector_performance, task_sentiment_analysis] >> task_serving_cache

# Layer 4: Metadata tracking (runs last)
task_serving_cache >> task_pipeline_metadata