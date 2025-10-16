"""
Gold Layer DAG - Analytics & ML Feature Engineering with Spark
Creates business intelligence views and ML-ready datasets

Author: Banking Portfolio Team
Version: 2.0 (Spark-enabled)
Date: October 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.dates import days_ago
import logging
import os
import json
import pandas as pd
import numpy as np

# Import custom utilities
import sys
sys.path.append('/opt/airflow/plugins')
from spark_utils import get_spark_manager, get_financial_processor, with_spark_session

# Default args
default_args = {
    'owner': 'banking-portfolio',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 16),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': int(os.getenv('MAX_RETRY_ATTEMPTS', 2)),
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# DAG definition
dag = DAG(
    'gold_layer_pipeline',
    default_args=default_args,
    description='Gold Layer - Analytics & ML Feature Engineering with Spark',
    schedule_interval='0 8 * * 1-5',  # 8:00 AM weekdays (after Silver DAG)
    catchup=False,
    max_active_runs=1,
    max_active_tasks=8,
    tags=['gold', 'analytics', 'spark', 'ml-features'],
)

def create_analytics_tables(**context):
    """Create business intelligence tables based on gold_layer_etl.py logic"""
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logging.info(f"📊 Creating analytics tables for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import json
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        results = {
            'market_summary_created': False,
            'stock_features_created': False,
            'news_sentiment_created': False,
            'execution_date': date_str
        }
        
        # 1. Create Market Summary from Silver stocks data
        try:
            # Read processed stock data from Silver layer - aligned with actual structure
            stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str.replace('-', '')}.csv"
            
            if not s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name):
                # Try alternative date format
                alt_stock_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
                if s3_hook.check_for_key(key=alt_stock_key, bucket_name=bucket_name):
                    stock_file_key = alt_stock_key
                else:
                    logging.warning(f"⚠️ No stock data found for market summary in either format")
                    return {'market_summary_created': False, 'execution_date': date_str}
                # Read silver stocks data
                csv_content = s3_hook.read_key(key=stock_file_key, bucket_name=bucket_name)
                stocks_df = pd.read_csv(pd.StringIO(csv_content))
                
                logging.info(f"📈 Processing {len(stocks_df)} stock records for market summary")
                
                # Create market summary aligned with Silver schema
                market_summary = {
                    'date': date_str,
                    'total_stocks': len(stocks_df),
                    'avg_close_price': float(stocks_df['close'].mean()) if len(stocks_df) > 0 else 0,
                    'total_volume': int(stocks_df['volume'].sum()) if len(stocks_df) > 0 else 0,
                    'avg_daily_return': float(stocks_df['daily_return'].mean() if 'daily_return' in stocks_df.columns else 0),
                    'price_gainers': len(stocks_df[stocks_df['daily_return'] > 0]) if 'daily_return' in stocks_df.columns and len(stocks_df) > 0 else 0,
                    'price_losers': len(stocks_df[stocks_df['daily_return'] < 0]) if 'daily_return' in stocks_df.columns and len(stocks_df) > 0 else 0,
                    'market_breadth_pct': (len(stocks_df[stocks_df['daily_return'] > 0]) / len(stocks_df) * 100) if 'daily_return' in stocks_df.columns and len(stocks_df) > 0 else 0,
                    'unique_symbols': int(stocks_df['symbol'].nunique()) if 'symbol' in stocks_df.columns else len(stocks_df),
                    '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
                }
                
                # Save market summary to Gold analytics
                market_summary_key = f"gold/analytics/market_summary/market_summary_{date_str.replace('-', '')}.json"
                s3_hook.load_string(
                    string_data=json.dumps(market_summary, ensure_ascii=False, indent=2),
                    key=market_summary_key,
                    bucket_name=bucket_name,
                    replace=True
                )
                
                results['market_summary_created'] = True
                logging.info(f"✅ Market summary created with {market_summary['total_stocks']} stocks")
                
            else:
                logging.warning(f"⚠️ No stock data found for market summary")
                
        except Exception as e:
            logging.error(f"❌ Market summary creation failed: {str(e)}")
        
        # 2. Create Stock Features for ML aligned with Silver schema
        try:
            if results['market_summary_created']:
                # Use existing stocks_df if market summary was created
                if 'stocks_df' in locals() and not stocks_df.empty:
                    # Create ML-ready features using actual Silver schema
                    ml_features = stocks_df.copy()
                    
                    # Ensure we have the required columns from Silver
                    if 'symbol' in ml_features.columns:
                        ml_features['ticker'] = ml_features['symbol']  # Standardize naming
                    
                    # Price-based features using actual Silver columns
                    if all(col in ml_features.columns for col in ['close', 'open']):
                        ml_features['price_change_pct'] = (ml_features['close'] - ml_features['open']) / ml_features['open']
                    
                    if all(col in ml_features.columns for col in ['high', 'low']):
                        ml_features['daily_range_pct'] = (ml_features['high'] - ml_features['low']) / ml_features['low']
                    
                    # Volume features
                    if 'volume' in ml_features.columns:
                        ml_features['volume_log'] = np.log1p(ml_features['volume'])
                        ml_features['volume_scaled'] = (ml_features['volume'] - ml_features['volume'].mean()) / ml_features['volume'].std()
                    
                    # Technical indicators from Silver (if available)
                    tech_columns = ['MA_5', 'MA_20', 'RSI', 'MACD', 'BB_position']
                    for col in tech_columns:
                        if col not in ml_features.columns:
                            ml_features[col] = 0  # Default values if not available
                    
                    # Banking sector classification
                    big4_banks = ['VCB', 'BID', 'CTG', 'AGR']
                    tier1_banks = ['VPB', 'TCB', 'MBB', 'STB', 'HDB', 'ACB']
                    
                    def classify_bank_tier(symbol):
                        symbol = str(symbol).upper()
                        if symbol in big4_banks:
                            return 'BIG_4'
                        elif symbol in tier1_banks:
                            return 'TIER_1'
                        else:
                            return 'TIER_2'
                    
                    symbol_col = 'symbol' if 'symbol' in ml_features.columns else 'ticker'
                    ml_features['bank_tier'] = ml_features[symbol_col].apply(classify_bank_tier)
                    
                    # Select final ML feature columns
                    feature_columns = ['symbol', 'date', 'close', 'volume', 'bank_tier']
                    if 'daily_return' in ml_features.columns:
                        feature_columns.append('daily_return')
                    if 'price_change_pct' in ml_features.columns:
                        feature_columns.append('price_change_pct')
                    if 'volume_log' in ml_features.columns:
                        feature_columns.append('volume_log')
                    
                    # Add technical indicators
                    feature_columns.extend([col for col in tech_columns if col in ml_features.columns])
                    
                    final_ml_features = ml_features[feature_columns].copy()
                    
                    # Save ML features to Gold serving
                    ml_features_csv = final_ml_features.to_csv(index=False)
                    ml_features_key = f"gold/serving/ml_features/ml_features_{date_str.replace('-', '')}.csv"
                s3_hook.load_string(
                    string_data=ml_features_csv,
                    key=ml_features_key,
                    bucket_name=bucket_name,
                    replace=True
                )
                
                results['stock_features_created'] = True
                logging.info(f"✅ ML features created for {len(stocks_df)} stocks")
                
        except Exception as e:
            logging.error(f"❌ Stock features creation failed: {str(e)}")
        
        # 3. Create News Sentiment Analytics aligned with Silver schema
        try:
            news_file_key = f"silver/news/processed/clean_news_{date_str.replace('-', '')}.csv"
            
            # Try alternative date format
            if not s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name):
                alt_news_key = f"silver/news/processed/clean_news_{date_str}.csv"
                if s3_hook.check_for_key(key=alt_news_key, bucket_name=bucket_name):
                    news_file_key = alt_news_key
            
            if s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name):
                # Read silver news data
                csv_content = s3_hook.read_key(key=news_file_key, bucket_name=bucket_name)
                news_df = pd.read_csv(pd.StringIO(csv_content))
                
                logging.info(f"📰 Processing {len(news_df)} news articles for sentiment analytics")
                
                # Create sentiment analytics using actual Silver schema
                sentiment_analytics = {
                    'date': date_str,
                    'total_articles': len(news_df),
                    'sentiment_distribution': {},
                    'topic_distribution': {},
                    'avg_content_length': 0,
                    'banking_articles': 0,
                    'positive_sentiment_ratio': 0,
                    '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
                }
                
                # Handle sentiment columns based on actual Silver output
                if 'sentiment_basic' in news_df.columns:
                    sentiment_analytics['sentiment_distribution'] = news_df['sentiment_basic'].value_counts().to_dict()
                    positive_count = len(news_df[news_df['sentiment_basic'] == 'POSITIVE'])
                    sentiment_analytics['positive_sentiment_ratio'] = (positive_count / len(news_df) * 100) if len(news_df) > 0 else 0
                elif 'sentiment_score' in news_df.columns:
                    # Create basic sentiment from scores
                    news_df['sentiment_basic'] = news_df['sentiment_score'].apply(
                        lambda x: 'POSITIVE' if x > 0.1 else ('NEGATIVE' if x < -0.1 else 'NEUTRAL')
                    )
                    sentiment_analytics['sentiment_distribution'] = news_df['sentiment_basic'].value_counts().to_dict()
                    positive_count = len(news_df[news_df['sentiment_basic'] == 'POSITIVE'])
                    sentiment_analytics['positive_sentiment_ratio'] = (positive_count / len(news_df) * 100) if len(news_df) > 0 else 0
                
                # Handle topic/category columns
                if 'topic_category' in news_df.columns:
                    sentiment_analytics['topic_distribution'] = news_df['topic_category'].value_counts().to_dict()
                    sentiment_analytics['banking_articles'] = len(news_df[news_df['topic_category'] == 'BANKING'])
                elif 'category' in news_df.columns:
                    sentiment_analytics['topic_distribution'] = news_df['category'].value_counts().to_dict()
                    sentiment_analytics['banking_articles'] = len(news_df[news_df['category'].str.contains('BANK', case=False, na=False)])
                
                # Handle content length
                if 'content_length' in news_df.columns:
                    sentiment_analytics['avg_content_length'] = float(news_df['content_length'].mean())
                elif 'combined_text' in news_df.columns:
                    news_df['content_length'] = news_df['combined_text'].str.len()
                    sentiment_analytics['avg_content_length'] = float(news_df['content_length'].mean())
                elif 'title' in news_df.columns:
                    news_df['content_length'] = news_df['title'].str.len()
                    sentiment_analytics['avg_content_length'] = float(news_df['content_length'].mean())
                
                # Save sentiment analytics
                sentiment_key = f"gold/analytics/sentiment_analysis/news_sentiment_{date_str.replace('-', '')}.json"
                s3_hook.load_string(
                    string_data=json.dumps(sentiment_analytics, ensure_ascii=False, indent=2),
                    key=sentiment_key,
                    bucket_name=bucket_name,
                    replace=True
                )
                
                results['news_sentiment_created'] = True
                logging.info(f"✅ News sentiment analytics created for {len(news_df)} articles")
                
            else:
                logging.warning(f"⚠️ No news data found for sentiment analytics")
                
        except Exception as e:
            logging.error(f"❌ News sentiment analytics failed: {str(e)}")
        
        # Create overall analytics metadata
        analytics_metadata = {
            'processing_date': date_str,
            'analytics_created': results,
            'gold_layer_structure': {
                'analytics_path': 'gold/analytics/',
                'serving_path': 'gold/serving/',
                'metadata_path': 'gold/metadata/'
            },
            '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
        }
        
        # Save analytics metadata
        metadata_key = f"gold/metadata/analytics_metadata_{date_str}.json"
        s3_hook.load_string(
            string_data=json.dumps(analytics_metadata, ensure_ascii=False, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        logging.info(f"✅ Analytics tables creation completed: {results}")
        return results
        
    except Exception as e:
        logging.error(f"💥 Analytics table creation failed: {str(e)}")
        raise

def create_ml_features(**context):
    """Create ML-ready feature datasets based on gold_layer_etl.py logic"""
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logging.info(f"🤖 Creating ML features for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import json
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        try:
            # Read processed stock data from Silver layer - aligned with actual structure
            stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str.replace('-', '')}.csv"
            
            if not s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name):
                # Try alternative date format
                alt_stock_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
                if s3_hook.check_for_key(key=alt_stock_key, bucket_name=bucket_name):
                    stock_file_key = alt_stock_key
                else:
                    logging.warning(f"⚠️ No stock data found for ML features")
                    return {'ml_features_records': 0, 'execution_date': date_str}
            
            # Read and process data
            csv_content = s3_hook.read_key(key=stock_file_key, bucket_name=bucket_name)
            df = pd.read_csv(pd.StringIO(csv_content))
            
            logging.info(f"🤖 Processing {len(df)} records for ML features")
            
            # Create ML features aligned with Silver schema
            ml_df = df.copy()
            
            # Standardize column names
            if 'symbol' in ml_df.columns and 'ticker' not in ml_df.columns:
                ml_df['ticker'] = ml_df['symbol']
            
            # Price-based features using available columns
            if all(col in ml_df.columns for col in ['close', 'open']):
                ml_df['price_to_open_ratio'] = ml_df['close'] / ml_df['open']
            
            if all(col in ml_df.columns for col in ['high', 'low']):
                ml_df['high_low_spread'] = (ml_df['high'] - ml_df['low']) / ml_df['low']
                ml_df['price_position'] = (ml_df['close'] - ml_df['low']) / (ml_df['high'] - ml_df['low'])
            
            # Volume features
            if 'volume' in ml_df.columns:
                ml_df['volume_log'] = np.log1p(ml_df['volume'])  # Log transform
                vol_mean = ml_df['volume'].mean()
                vol_std = ml_df['volume'].std()
                if vol_std > 0:
                    ml_df['volume_scaled'] = (ml_df['volume'] - vol_mean) / vol_std
                else:
                    ml_df['volume_scaled'] = 0
            
            # Return-based features
            if 'daily_return' in ml_df.columns:
                ml_df['return_squared'] = ml_df['daily_return'] ** 2
                ml_df['return_positive'] = (ml_df['daily_return'] > 0).astype(int)
                ml_df['return_abs'] = abs(ml_df['daily_return'])
            else:
                # Calculate daily return if not present
                if all(col in ml_df.columns for col in ['close', 'open']):
                    ml_df['daily_return'] = (ml_df['close'] - ml_df['open']) / ml_df['open']
                    ml_df['return_squared'] = ml_df['daily_return'] ** 2
                    ml_df['return_positive'] = (ml_df['daily_return'] > 0).astype(int)
                    ml_df['return_abs'] = abs(ml_df['daily_return'])
            
            # Banking sector encoding
            big4_banks = ['VCB', 'BID', 'CTG', 'AGR']
            tier1_banks = ['VPB', 'TCB', 'MBB', 'STB', 'HDB', 'ACB', 'TPB', 'VIB']
            
            def encode_bank_tier(ticker):
                ticker = str(ticker).upper()
                if ticker in big4_banks:
                    return 1.0  # Highest tier
                elif ticker in tier1_banks:
                    return 0.7  # Medium tier
                else:
                    return 0.3  # Lower tier
            
            ticker_col = 'ticker' if 'ticker' in ml_df.columns else 'symbol'
            ml_df['bank_tier_score'] = ml_df[ticker_col].apply(encode_bank_tier)
            
            # Technical signal encoding (use defaults if not available)
            if 'trend_signal' in ml_df.columns:
                ml_df['is_bullish'] = (ml_df['trend_signal'] == 'BULLISH').astype(int)
                ml_df['is_bearish'] = (ml_df['trend_signal'] == 'BEARISH').astype(int)
            else:
                ml_df['is_bullish'] = 0
                ml_df['is_bearish'] = 0
            
            if 'rsi_signal' in ml_df.columns:
                ml_df['rsi_overbought'] = (ml_df['rsi_signal'] == 'OVERBOUGHT').astype(int)
                ml_df['rsi_oversold'] = (ml_df['rsi_signal'] == 'OVERSOLD').astype(int)
            else:
                ml_df['rsi_overbought'] = 0
                ml_df['rsi_oversold'] = 0
            
            # Target variables for supervised learning
            if 'daily_return' in ml_df.columns:
                ml_df['target_direction'] = ml_df['daily_return'].apply(
                    lambda x: 'UP' if x > 0.02 else ('DOWN' if x < -0.02 else 'FLAT')
                )
                ml_df['target_volatility'] = ml_df['return_abs'] if 'return_abs' in ml_df.columns else abs(ml_df['daily_return'])
            else:
                ml_df['target_direction'] = 'FLAT'
                ml_df['target_volatility'] = 0
            
            # Select ML-ready features (only include columns that exist)
            base_columns = ['ticker', 'date', 'close', 'volume', 'daily_return']
            feature_columns = [col for col in base_columns if col in ml_df.columns]
            
            additional_features = [
                'price_to_open_ratio', 'high_low_spread', 'price_position',
                'volume_log', 'volume_scaled', 'return_squared', 'return_positive',
                'return_abs', 'bank_tier_score', 'is_bullish', 'is_bearish',
                'rsi_overbought', 'rsi_oversold', 'target_direction', 'target_volatility'
            ]
            
            for col in additional_features:
                if col in ml_df.columns:
                    feature_columns.append(col)
            
            # Filter columns that exist and create final ML features
            ml_features_df = ml_df[feature_columns].copy()
            
            # Add metadata
            ml_features_df['_ml_features_version'] = '2.0'
            ml_features_df['_created_at_utc'] = pd.Timestamp.utcnow().isoformat() + 'Z'
            
            # Save ML features
            ml_csv_content = ml_features_df.to_csv(index=False)
            ml_features_key = f"gold/serving/ml_features/ml_features_{date_str.replace('-', '')}.csv"
            
            s3_hook.load_string(
                string_data=ml_csv_content,
                key=ml_features_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Create feature statistics for monitoring
            feature_stats = {
                'total_samples': len(ml_features_df),
                'feature_count': len(feature_columns),
                'target_distribution': ml_features_df['target_direction'].value_counts().to_dict() if 'target_direction' in ml_features_df.columns else {},
                'avg_return': float(ml_features_df['daily_return'].mean()) if 'daily_return' in ml_features_df.columns else 0,
                'return_volatility': float(ml_features_df['daily_return'].std()) if 'daily_return' in ml_features_df.columns else 0,
                'bank_tier_distribution': ml_features_df['bank_tier_score'].value_counts().to_dict() if 'bank_tier_score' in ml_features_df.columns else {},
                'processing_date': date_str,
                '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
            }
            
            # Save feature statistics
            stats_key = f"gold/metadata/feature_stats/feature_stats_{date_str.replace('-', '')}.json"
            s3_hook.load_string(
                string_data=json.dumps(feature_stats, ensure_ascii=False, indent=2),
                key=stats_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            result = {
                'ml_features_records': len(ml_features_df),
                'feature_columns': len(feature_columns),
                'target_up_count': len(ml_features_df[ml_features_df['target_direction'] == 'UP']) if 'target_direction' in ml_features_df.columns else 0,
                'target_down_count': len(ml_features_df[ml_features_df['target_direction'] == 'DOWN']) if 'target_direction' in ml_features_df.columns else 0,
                'execution_date': date_str
            }
            
            logging.info(f"✅ ML features created successfully: {result}")
            return result
            
        except Exception as e:
            logging.error(f"❌ ML features creation failed: {str(e)}")
            return {'ml_features_records': 0, 'execution_date': date_str}
        
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
