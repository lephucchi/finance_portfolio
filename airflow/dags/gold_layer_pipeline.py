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

sys.path.append('/opt/airflow/dags')
from utils.sector_mapping import get_sector, SECTOR_MAPPING, SECTOR_INFO
# Removed enhanced_logger import for simplified testing

# Configuration
S3_BUCKET = 'bankanalystportfolio'
S3_CONN_ID = 'aws_s3_conn'

# Default arguments
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
    'gold_layer_pipeline',
    default_args=default_args,
    description='Gold layer - 4-layer analytics architecture',
    schedule_interval='0 8 * * 1-5',  # 8 AM weekdays
    catchup=False,
    tags=['gold', 'lakehouse', 'analytics'],
    max_active_runs=1
)

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for stock data"""
    # Rename 'time' to 'data_date' if needed
    if 'time' in df.columns and 'data_date' not in df.columns:
        df = df.rename(columns={'time': 'data_date'})
    
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
    
    # Price change percentage
    df['price_change_pct'] = df['close'].pct_change() * 100
    
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
        start_date = end_date - timedelta(days=1)  # Only 2 days: yesterday + today
        
        logging.info(f"📅 Processing stocks for LAST 2 DAYS: {start_date} to {end_date}")
        
        # List all stock files in Silver layer for last 2 days only
        silver_prefix = 'silver/stocks/'
        all_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=silver_prefix)
        
        if not all_files:
            logging.warning("No Silver stock files found")
            return
        
        # Filter parquet files in date range (ONLY 2 days)
        stock_files = [f for f in all_files if f.endswith('.parquet') and 'partition_date=' in f]
        all_stocks = []
        
        # Read stock files for 2 days only
        for file_key in stock_files:
            try:
                # Extract partition date
                partition_str = file_key.split('partition_date=')[1].split('/')[0]
                partition_date = datetime.strptime(partition_str, '%Y-%m-%d').date()
                
                # ONLY accept yesterday and today
                if partition_date == start_date or partition_date == end_date:
                    obj = s3_hook.get_key(file_key, bucket_name=S3_BUCKET)
                    parquet_data = obj.get()['Body'].read()
                    df = pd.read_parquet(BytesIO(parquet_data))
                    all_stocks.append(df)
                    logging.info(f"  ✅ Loaded {len(df)} records from {partition_date}")
            except Exception as e:
                logging.error(f"Error reading {file_key}: {e}")
                continue
        
        if not all_stocks:
            logging.warning("No stock data in date range")
            return
        
        # Combine all stocks
        stocks_df = pd.concat(all_stocks, ignore_index=True)
        
        # Rename 'ticker' to 'symbol' for consistency
        if 'ticker' in stocks_df.columns:
            stocks_df = stocks_df.rename(columns={'ticker': 'symbol'})
        
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
    Layer 1 - ANALYTICS: Create sector_performance table (ENHANCED with 10+ sectors)
    Input: gold/analytics/market_features/partition_date=*/
    Output: gold/analytics/sector_performance/partition_date=YYYY-MM-DD/*.parquet
    
    Enhanced metrics:
    - 13 sectors (Banking, Technology, Real Estate, Energy, Materials, Consumer, etc.)
    - Advanced metrics: market_cap_change, sector_momentum, top gainers/losers
    """
    execution_date = context['execution_date']
    logging.info("🚀 Starting sector performance aggregation")
    
    try:
        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
        end_date = execution_date.date()
        partition_date_str = end_date.strftime('%Y-%m-%d')
        
        # Read market features
        market_prefix = f'gold/analytics/market_features/partition_date={partition_date_str}/'
        market_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=market_prefix)
        market_parquet = [f for f in market_files if f.endswith('.parquet')]
        
        if not market_parquet:
            logging.warning("⚠️ No market features found")
            return
        
        obj = s3_hook.get_key(market_parquet[0], bucket_name=S3_BUCKET)
        market_df = pd.read_parquet(BytesIO(obj.get()['Body'].read()))
        
        logging.info(f"📊 Loaded {len(market_df)} stocks for sector analysis")
        
        # Map stocks to sectors using enhanced mapping
        market_df['sector'] = market_df['symbol'].apply(get_sector)
        
        # Count stocks per sector
        sector_counts = market_df['sector'].value_counts()
        logging.info(f"🏢 Sector distribution: {sector_counts.to_dict()}")
        
        # Calculate comprehensive sector aggregations
        sector_metrics = []
        
        for sector in market_df['sector'].unique():
            sector_stocks = market_df[market_df['sector'] == sector]
            
            # Basic metrics
            avg_price_change = sector_stocks['price_change_pct'].mean()
            avg_volatility = sector_stocks['volatility_7d'].mean() if 'volatility_7d' in sector_stocks.columns else 0
            total_volume = sector_stocks['volume'].sum()
            avg_volume = sector_stocks['volume'].mean()
            
            # Market cap change (if available)
            market_cap_change = 0
            if 'market_cap' in sector_stocks.columns and 'price_change_pct' in sector_stocks.columns:
                market_cap_change = (sector_stocks['market_cap'] * sector_stocks['price_change_pct'] / 100).sum()
            
            # Sector momentum (weighted by volume)
            sector_momentum = 0
            if 'volume' in sector_stocks.columns and 'price_change_pct' in sector_stocks.columns:
                total_vol = sector_stocks['volume'].sum()
                if total_vol > 0:
                    sector_momentum = (sector_stocks['price_change_pct'] * sector_stocks['volume']).sum() / total_vol
            
            # Top gainers and losers
            top_3_gainers = sector_stocks.nlargest(3, 'price_change_pct')['symbol'].tolist()
            top_3_losers = sector_stocks.nsmallest(3, 'price_change_pct')['symbol'].tolist()
            
            # Stock counts
            stocks_up = len(sector_stocks[sector_stocks['price_change_pct'] > 0])
            stocks_down = len(sector_stocks[sector_stocks['price_change_pct'] < 0])
            stocks_unchanged = len(sector_stocks[sector_stocks['price_change_pct'] == 0])
            
            sector_metrics.append({
                'sector': sector,
                'sector_name_vi': SECTOR_INFO.get(sector, {}).get('name_vi', sector),
                'avg_price_change_pct': round(avg_price_change, 2),
                'avg_volatility': round(avg_volatility, 2),
                'total_volume': int(total_volume),
                'avg_volume': int(avg_volume),
                'market_cap_change': round(market_cap_change, 2),
                'sector_momentum': round(sector_momentum, 2),
                'stocks_count': len(sector_stocks),
                'stocks_up': stocks_up,
                'stocks_down': stocks_down,
                'stocks_unchanged': stocks_unchanged,
                'top_3_gainers': ','.join(top_3_gainers),
                'top_3_losers': ','.join(top_3_losers),
                'data_date': end_date
            })
        
        sector_agg = pd.DataFrame(sector_metrics)
        
        # Sort by sector momentum (strongest sectors first)
        sector_agg = sector_agg.sort_values('sector_momentum', ascending=False)
        
        # Write to Gold analytics layer
        gold_prefix = f'gold/analytics/sector_performance/partition_date={partition_date_str}/'
        
        parquet_buffer = BytesIO()
        sector_agg.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
        parquet_buffer.seek(0)
        
        s3_key = f'{gold_prefix}sector_performance_{end_date.strftime("%Y%m%d")}.parquet'
        s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)
        
        logging.info(f"✅ Sector performance created: {len(sector_agg)} sectors")
        logging.info(f"📈 Top performing sector: {sector_agg.iloc[0]['sector']} ({sector_agg.iloc[0]['sector_momentum']:.2f}%)")
        logging.info(f"📉 Weakest sector: {sector_agg.iloc[-1]['sector']} ({sector_agg.iloc[-1]['sector_momentum']:.2f}%)")
        
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
    Layer 1 - ANALYTICS: Create macro_indicators with daily partition (FIXED)
    Input: silver/macro/partition_date=YYYY-MM-DD/macro_data.parquet
    Output: gold/analytics/macro_indicators/partition_date=YYYY-MM-DD/*.parquet
    
    Creates NEW partition for each execution_date (not re-reading 30 days history)
    """
    execution_date = context['execution_date']
    logging.info("🚀 Starting macro indicators daily partition")
    
    try:
        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
        end_date = execution_date.date()
        partition_date_str = end_date.strftime('%Y-%m-%d')
        
        # Read ONLY today's macro data from Silver
        macro_prefix = f'silver/macro/partition_date={partition_date_str}/'
        macro_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=macro_prefix)
        macro_parquet = [f for f in macro_files if f.endswith('.parquet')]
        
        if not macro_parquet:
            logging.warning(f"⚠️ No macro data found for {partition_date_str}")
            return
        
        obj = s3_hook.get_key(macro_parquet[0], bucket_name=S3_BUCKET)
        macro_df = pd.read_parquet(BytesIO(obj.get()['Body'].read()))
        
        logging.info(f"📊 Loaded {len(macro_df)} macro indicators for {partition_date_str}")
        
        # Add partition date to output
        macro_df['data_date'] = end_date
        macro_df['partition_date'] = partition_date_str
        
        # Write to Gold analytics layer with NEW partition
        gold_prefix = f'gold/analytics/macro_indicators/partition_date={partition_date_str}/'
        
        parquet_buffer = BytesIO()
        macro_df.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
        parquet_buffer.seek(0)
        
        s3_key = f'{gold_prefix}macro_indicators_{end_date.strftime("%Y%m%d")}.parquet'
        s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)
        
        logging.info(f"✅ Macro indicators created: {len(macro_df)} indicators for partition {partition_date_str}")
        
    except Exception as e:
        logging.error(f"❌ Macro indicators failed: {str(e)}")
        raise


# ========================================
# LAYER 2 - SENTIMENT ANALYSIS
# ========================================
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
    Layer 2 - SENTIMENT_ANALYSIS: Aggregate news sentiment (FIXED - use Silver sentiment)
    Input: silver/news/partition_date=*/news_cleaned.parquet (with sentiment_score from Silver)
    Output: gold/sentiment_analysis/partition_date=YYYY-MM-DD/*.parquet
    
    NOW USES REAL SENTIMENT from Silver layer (not hardcoded 0)
    """
    execution_date = context['execution_date']
    logging.info("🚀 Starting sentiment analysis aggregation")
    
    try:
        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)
        end_date = execution_date.date()
        partition_date_str = end_date.strftime('%Y-%m-%d')
        
        # Read ONLY TODAY's news with sentiment from Silver
        news_prefix = f'silver/news/partition_date={partition_date_str}/'
        news_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=news_prefix)
        news_parquet = [f for f in news_files if f.endswith('.parquet')]
        
        if not news_parquet:
            logging.warning(f"⚠️ No news data found for {partition_date_str}")
            return
        
        obj = s3_hook.get_key(news_parquet[0], bucket_name=S3_BUCKET)
        news_df = pd.read_parquet(BytesIO(obj.get()['Body'].read()))
        
        logging.info(f"📰 Loaded {len(news_df)} news articles for {partition_date_str}")
        
        # Ensure we have sentiment_score (should be from Silver)
        if 'sentiment_score' not in news_df.columns:
            logging.warning("⚠️ No sentiment_score column - using 0")
            news_df['sentiment_score'] = 0.0
        else:
            logging.info(f"✅ Using REAL sentiment scores from Silver (avg={news_df['sentiment_score'].mean():.2f})")
        
        # Ensure source column exists
        if 'source' not in news_df.columns:
            news_df['source'] = 'unknown'
        
        # Aggregate sentiment by source
        sentiment_by_source = []
        for source in news_df['source'].unique():
            source_news = news_df[news_df['source'] == source]
            
            sentiment_by_source.append({
                'data_date': end_date,
                'source': source,
                'avg_sentiment': round(source_news['sentiment_score'].mean(), 2),
                'article_count': len(source_news),
                'positive_count': len(source_news[source_news['sentiment_score'] > 0]),
                'negative_count': len(source_news[source_news['sentiment_score'] < 0]),
                'neutral_count': len(source_news[source_news['sentiment_score'] == 0]),
                'max_sentiment': round(source_news['sentiment_score'].max(), 2),
                'min_sentiment': round(source_news['sentiment_score'].min(), 2)
            })
        
        sentiment_agg = pd.DataFrame(sentiment_by_source)
        
        # Sort by avg_sentiment descending
        sentiment_agg = sentiment_agg.sort_values('avg_sentiment', ascending=False)
        
        # Write to Gold sentiment_analysis layer
        gold_prefix = f'gold/sentiment_analysis/partition_date={partition_date_str}/'
        
        parquet_buffer = BytesIO()
        sentiment_agg.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)
        parquet_buffer.seek(0)
        
        s3_key = f'{gold_prefix}sentiment_analysis_{end_date.strftime("%Y%m%d")}.parquet'
        s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)
        
        logging.info(f"✅ Sentiment analysis created: {len(sentiment_agg)} sources")
        logging.info(f"📊 Overall avg sentiment: {news_df['sentiment_score'].mean():.2f}")
        logging.info(f"📈 Most positive source: {sentiment_agg.iloc[0]['source']} ({sentiment_agg.iloc[0]['avg_sentiment']:.2f})")
        
    except Exception as e:
        logging.error(f"❌ Sentiment analysis failed: {str(e)}")
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