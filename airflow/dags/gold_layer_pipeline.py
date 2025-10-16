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
            stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
            
            if s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name):
                # Read silver stocks data
                csv_content = s3_hook.read_key(key=stock_file_key, bucket_name=bucket_name)
                stocks_df = pd.read_csv(pd.StringIO(csv_content))
                
                logging.info(f"📈 Processing {len(stocks_df)} stock records for market summary")
                
                # Create market summary (from gold_layer_etl.py)
                market_summary = {
                    'date': date_str,
                    'total_stocks': len(stocks_df),
                    'avg_price': float(stocks_df['close'].mean()) if len(stocks_df) > 0 else 0,
                    'total_volume': int(stocks_df['volume'].sum()) if len(stocks_df) > 0 else 0,
                    'avg_daily_return': float(stocks_df['daily_return'].mean()) if len(stocks_df) > 0 else 0,
                    'price_gainers': len(stocks_df[stocks_df['daily_return'] > 0]) if len(stocks_df) > 0 else 0,
                    'price_losers': len(stocks_df[stocks_df['daily_return'] < 0]) if len(stocks_df) > 0 else 0,
                    'unchanged': len(stocks_df[stocks_df['daily_return'] == 0]) if len(stocks_df) > 0 else 0,
                    'market_breadth': (len(stocks_df[stocks_df['daily_return'] > 0]) / len(stocks_df) * 100) if len(stocks_df) > 0 else 0,
                    '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
                }
                
                # Save market summary
                market_summary_key = f"gold/analytics/market_summary_{date_str}.json"
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
        
        # 2. Create Stock Features for ML (from gold_layer_etl.py)
        try:
            if results['market_summary_created']:
                # Create ML-ready features
                stocks_df['price_change_pct'] = stocks_df['daily_return']
                stocks_df['volume_normalized'] = (stocks_df['volume'] - stocks_df['volume'].mean()) / stocks_df['volume'].std()
                stocks_df['price_momentum'] = stocks_df['close'] - stocks_df['open']
                stocks_df['volatility_score'] = abs(stocks_df['daily_return'])
                
                # Banking tier classification
                big4_banks = ['VCB', 'BID', 'CTG', 'AGR']
                tier1_banks = ['VPB', 'TCB', 'MBB', 'STB', 'HDB', 'ACB']
                
                def classify_bank_tier(ticker):
                    if ticker in big4_banks:
                        return 'BIG_4'
                    elif ticker in tier1_banks:
                        return 'TIER_1'
                    else:
                        return 'TIER_2'
                
                stocks_df['bank_tier'] = stocks_df['ticker'].apply(classify_bank_tier)
                
                # Save ML features
                ml_features_csv = stocks_df[['ticker', 'date', 'close', 'volume', 'daily_return', 
                                           'price_change_pct', 'volume_normalized', 'price_momentum',
                                           'volatility_score', 'bank_tier']].to_csv(index=False)
                
                ml_features_key = f"gold/serving/ml_features_{date_str}.csv"
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
        
        # 3. Create News Sentiment Analytics (from gold_layer_etl.py)
        try:
            news_file_key = f"silver/news/processed/clean_news_{date_str}.csv"
            
            if s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name):
                # Read silver news data
                csv_content = s3_hook.read_key(key=news_file_key, bucket_name=bucket_name)
                news_df = pd.read_csv(pd.StringIO(csv_content))
                
                logging.info(f"📰 Processing {len(news_df)} news articles for sentiment analytics")
                
                # Create sentiment analytics
                sentiment_analytics = {
                    'date': date_str,
                    'total_articles': len(news_df),
                    'sentiment_distribution': news_df['sentiment_basic'].value_counts().to_dict(),
                    'topic_distribution': news_df['topic_category'].value_counts().to_dict(),
                    'avg_content_length': float(news_df['content_length'].mean()) if len(news_df) > 0 else 0,
                    'banking_articles': len(news_df[news_df['topic_category'] == 'BANKING']) if len(news_df) > 0 else 0,
                    'positive_sentiment_ratio': (len(news_df[news_df['sentiment_basic'] == 'POSITIVE']) / len(news_df) * 100) if len(news_df) > 0 else 0,
                    '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
                }
                
                # Save sentiment analytics
                sentiment_key = f"gold/analytics/news_sentiment_{date_str}.json"
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
            # Read processed stock data from Silver layer
            stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
            
            if not s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name):
                logging.warning(f"⚠️ No stock data found for ML features")
                return {'ml_features_records': 0, 'execution_date': date_str}
            
            # Read and process data
            csv_content = s3_hook.read_key(key=stock_file_key, bucket_name=bucket_name)
            df = pd.read_csv(pd.StringIO(csv_content))
            
            logging.info(f"🤖 Processing {len(df)} records for ML features")
            
            # Create ML features (from gold_layer_etl.py)
            ml_df = df.copy()
            
            # Price-based features
            ml_df['price_to_open_ratio'] = ml_df['close'] / ml_df['open']
            ml_df['high_low_spread'] = (ml_df['high'] - ml_df['low']) / ml_df['low']
            ml_df['price_position'] = (ml_df['close'] - ml_df['low']) / (ml_df['high'] - ml_df['low'])
            
            # Volume features
            ml_df['volume_log'] = np.log1p(ml_df['volume'])  # Log transform to handle large values
            ml_df['volume_scaled'] = (ml_df['volume'] - ml_df['volume'].mean()) / ml_df['volume'].std()
            
            # Return-based features
            ml_df['return_squared'] = ml_df['daily_return'] ** 2  # For volatility modeling
            ml_df['return_positive'] = (ml_df['daily_return'] > 0).astype(int)
            ml_df['return_abs'] = abs(ml_df['daily_return'])
            
            # Banking sector encoding
            big4_banks = ['VCB', 'BID', 'CTG', 'AGR']
            tier1_banks = ['VPB', 'TCB', 'MBB', 'STB', 'HDB', 'ACB', 'TPB', 'VIB']
            
            def encode_bank_tier(ticker):
                if ticker in big4_banks:
                    return 1.0  # Highest tier
                elif ticker in tier1_banks:
                    return 0.7  # Medium tier
                else:
                    return 0.3  # Lower tier
            
            ml_df['bank_tier_score'] = ml_df['ticker'].apply(encode_bank_tier)
            
            # Technical signal encoding
            ml_df['is_bullish'] = (ml_df['trend_signal'] == 'BULLISH').astype(int)
            ml_df['is_bearish'] = (ml_df['trend_signal'] == 'BEARISH').astype(int)
            ml_df['rsi_overbought'] = (ml_df['rsi_signal'] == 'OVERBOUGHT').astype(int)
            ml_df['rsi_oversold'] = (ml_df['rsi_signal'] == 'OVERSOLD').astype(int)
            
            # Target variables for supervised learning (simplified for single day)
            ml_df['target_direction'] = ml_df['daily_return'].apply(
                lambda x: 'UP' if x > 0.02 else ('DOWN' if x < -0.02 else 'FLAT')
            )
            ml_df['target_volatility'] = ml_df['return_abs']
            
            # Select ML-ready features
            feature_columns = [
                'ticker', 'date', 'close', 'volume', 'daily_return',
                'price_to_open_ratio', 'high_low_spread', 'price_position',
                'volume_log', 'volume_scaled', 'return_squared', 'return_positive',
                'return_abs', 'bank_tier_score', 'is_bullish', 'is_bearish',
                'rsi_overbought', 'rsi_oversold', 'target_direction', 'target_volatility'
            ]
            
            # Filter columns that exist
            available_columns = [col for col in feature_columns if col in ml_df.columns]
            ml_features_df = ml_df[available_columns].copy()
            
            # Add metadata
            ml_features_df['_ml_features_version'] = '1.0'
            ml_features_df['_created_at_utc'] = pd.Timestamp.utcnow().isoformat() + 'Z'
            
            # Save ML features
            ml_csv_content = ml_features_df.to_csv(index=False)
            ml_features_key = f"gold/serving/ml_features_{date_str}.csv"
            
            s3_hook.load_string(
                string_data=ml_csv_content,
                key=ml_features_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Create feature statistics for monitoring
            feature_stats = {
                'total_samples': len(ml_features_df),
                'feature_count': len(available_columns),
                'target_distribution': ml_features_df['target_direction'].value_counts().to_dict(),
                'avg_return': float(ml_features_df['daily_return'].mean()),
                'return_volatility': float(ml_features_df['daily_return'].std()),
                'bank_tier_distribution': ml_features_df['bank_tier_score'].value_counts().to_dict(),
                'processing_date': date_str,
                '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
            }
            
            # Save feature statistics
            stats_key = f"gold/metadata/feature_stats_{date_str}.json"
            s3_hook.load_string(
                string_data=json.dumps(feature_stats, ensure_ascii=False, indent=2),
                key=stats_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            result = {
                'ml_features_records': len(ml_features_df),
                'feature_columns': len(available_columns),
                'target_up_count': len(ml_features_df[ml_features_df['target_direction'] == 'UP']),
                'target_down_count': len(ml_features_df[ml_features_df['target_direction'] == 'DOWN']),
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
            # Read stock data
            stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
            has_stocks = s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name)
            
            # Read news data
            news_file_key = f"silver/news/processed/clean_news_{date_str}.csv"
            has_news = s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name)
            
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
                    
                    # Aggregate news sentiment by date
                    daily_sentiment = {
                        'total_articles': len(news_df),
                        'positive_articles': len(news_df[news_df['sentiment_basic'] == 'POSITIVE']),
                        'negative_articles': len(news_df[news_df['sentiment_basic'] == 'NEGATIVE']),
                        'neutral_articles': len(news_df[news_df['sentiment_basic'] == 'NEUTRAL']),
                        'banking_articles': len(news_df[news_df['topic_category'] == 'BANKING']),
                        'avg_content_length': float(news_df['content_length'].mean()) if len(news_df) > 0 else 0
                    }
                    
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
            
            # Save integrated view
            integrated_csv_content = integrated_df.to_csv(index=False)
            integrated_key = f"gold/serving/integrated_view_{date_str}.csv"
            
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
                'unique_stocks': integrated_df['ticker'].nunique(),
                'has_news_data': has_news,
                'market_summary': {
                    'avg_return': float(integrated_df['daily_return'].mean()),
                    'total_volume': int(integrated_df['volume'].sum()),
                    'avg_sentiment_score': float(integrated_df['news_sentiment_score'].mean())
                },
                'sector_distribution': integrated_df['bank_sector'].value_counts().to_dict(),
                '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
            }
            
            # Save integrated summary
            summary_key = f"gold/metadata/integrated_summary_{date_str}.json"
            s3_hook.load_string(
                string_data=json.dumps(integrated_summary, ensure_ascii=False, indent=2),
                key=summary_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            result = {
                'integrated_records': len(integrated_df),
                'has_news_data': has_news,
                'unique_stocks': integrated_df['ticker'].nunique(),
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
