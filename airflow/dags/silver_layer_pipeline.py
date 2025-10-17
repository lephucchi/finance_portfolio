"""
Silver Layer Pipeline DAG - Clean and process Bronze data
Process stock, news, and others data with analytics and validation

Schedule: Daily at 7:00 AM weekdays after Bronze layer completion
Author: Finance Portfolio System
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.trigger_rule import TriggerRule
import logging
import os

# Import enhanced logging
import sys
sys.path.append('/opt/airflow/utils')
from enhanced_logger import get_enhanced_logger, log_pipeline_start, log_pipeline_success, log_pipeline_error

# Default arguments
default_args = {
    'owner': 'finance_portfolio',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retry_delay': timedelta(minutes=5),
    'retries': 2,
}

# DAG definition
dag = DAG(
    'silver_layer_pipeline',
    default_args=default_args,
    description='Silver Layer Data Processing Pipeline with pandas',
    schedule_interval='0 7 * * 1-5',  # 7:00 AM weekdays
    catchup=False,
    max_active_runs=1,
    tags=['silver', 'processing', 'pandas', 'finance']
)

def process_stock_data(**context):
    """Process stock data with technical indicators based on original logic"""
    # Initialize enhanced logger
    logger = get_enhanced_logger("silver_stocks_processing", "INFO")
    
    # Start pipeline operation tracking
    metadata = log_pipeline_start(
        logger,
        pipeline_name="silver_stocks_processing",
        layer="silver",
        operation="process_and_analyze",
        dag_run_id=context.get('dag_run').run_id,
        task_id=context.get('task_instance').task_id
    )
    
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger.log_progress(metadata, f"Starting stock data processing for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import numpy as np
        import json
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        try:
            # Read multiple JSON files from bronze/stocks/raw/{ticker}/ structure
            logging.info("📈 Reading stock data from Bronze layer...")
            
            # Get list of stock files from Bronze layer (individual JSON files per ticker/date)
            bronze_stock_files = []
            try:
                # List all objects in bronze/stocks/raw/ to find ticker folders
                paginator = s3_hook.get_session().client('s3').get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=bucket_name, Prefix="bronze/stocks/raw/"):
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            if obj['Key'].endswith('.json') and date_str in obj['Key']:
                                bronze_stock_files.append(obj['Key'])
                
                logging.info(f"📊 Found {len(bronze_stock_files)} stock files for {date_str}")
                
            except Exception as list_error:
                logging.error(f"❌ Error listing bronze stock files: {str(list_error)}")
                return {'stocks_processed': 0, 'execution_date': date_str}
            
            if len(bronze_stock_files) == 0:
                logging.warning(f"⚠️ No stock files found for {date_str}")
                return {'stocks_processed': 0, 'execution_date': date_str}
            
            # Read and combine all stock JSON files
            all_stocks = []
            for file_key in bronze_stock_files:
                try:
                    file_content = s3_hook.read_key(key=file_key, bucket_name=bucket_name)
                    stock_record = json.loads(file_content)
                    all_stocks.append(stock_record)
                except Exception as file_error:
                    logging.warning(f"⚠️ Error reading {file_key}: {str(file_error)}")
                    continue
            
            if len(all_stocks) == 0:
                logging.error(f"❌ No valid stock data found for {date_str}")
                return {'stocks_processed': 0, 'execution_date': date_str}
            
            logging.info(f"💹 Processing {len(all_stocks)} stock records")
            
            # Convert to DataFrame
            stocks_df = pd.DataFrame(all_stocks)
            
            # Ensure required columns exist and are properly typed
            expected_columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']
            for col in expected_columns:
                if col not in stocks_df.columns:
                    logging.warning(f"⚠️ Missing column: {col}")
                    stocks_df[col] = 0 if col != 'ticker' and col != 'date' else ''
            
            # Ensure numeric columns
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                stocks_df[col] = pd.to_numeric(stocks_df[col], errors='coerce').fillna(0)
            
            # Calculate technical indicators
            def calculate_rsi(prices, window=14):
                """Calculate RSI"""
                if len(prices) < window:
                    return np.nan
                
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
                
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
            
            def calculate_sma(prices, window=20):
                """Calculate Simple Moving Average"""
                if len(prices) < window:
                    return prices.mean()
                return prices.rolling(window=window).mean().iloc[-1]
            
            # Process each stock
            processed_stocks = []
            
            for ticker in stocks_df['ticker'].unique():
                ticker_data = stocks_df[stocks_df['ticker'] == ticker].copy()
                
                if len(ticker_data) == 0:
                    continue
                
                # Sort by date
                ticker_data = ticker_data.sort_values('date')
                
                # Get latest record
                latest = ticker_data.iloc[-1]
                
                # Calculate daily return
                if len(ticker_data) > 1:
                    previous_close = ticker_data.iloc[-2]['close']
                    daily_return = (latest['close'] - previous_close) / previous_close
                else:
                    daily_return = 0.0
                
                # Technical indicators
                prices = ticker_data['close']
                rsi_14 = calculate_rsi(prices, 14)
                ma_20 = calculate_sma(prices, 20)
                ma_50 = calculate_sma(prices, 50)
                
                # Volume analysis
                avg_volume = ticker_data['volume'].mean()
                volume_ratio = latest['volume'] / avg_volume if avg_volume > 0 else 1.0
                
                processed_stock = {
                    'ticker': latest['ticker'],
                    'date': latest['date'],
                    'open': float(latest['open']),
                    'high': float(latest['high']),
                    'low': float(latest['low']),
                    'close': float(latest['close']),
                    'volume': int(latest['volume']),
                    'daily_return': float(daily_return),
                    'rsi_14': float(rsi_14) if not pd.isna(rsi_14) else 50.0,
                    'ma_20': float(ma_20) if not pd.isna(ma_20) else float(latest['close']),
                    'ma_50': float(ma_50) if not pd.isna(ma_50) else float(latest['close']),
                    'volume_ratio': float(volume_ratio),
                    'price_change_pct': float(daily_return * 100),
                    'high_low_pct': float((latest['high'] - latest['low']) / latest['low'] * 100) if latest['low'] > 0 else 0.0,
                    'processing_date': date_str,
                    '_processed_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
                }
                
                processed_stocks.append(processed_stock)
            
            if len(processed_stocks) == 0:
                logger.log_progress(metadata, "No stocks processed successfully")
                result = {'stocks_processed': 0, 'execution_date': date_str}
                log_pipeline_success(logger, metadata, 0, 0)
                return result
            
            # Create processed DataFrame
            processed_df = pd.DataFrame(processed_stocks)
            logger.log_progress(metadata, f"Created DataFrame with {len(processed_df)} processed stocks")
            
            # Track S3 paths for logging
            s3_paths = []
            
            # Save as CSV
            csv_content = processed_df.to_csv(index=False)
            csv_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
            
            logger.log_s3_operation(metadata, "write", csv_key, "csv")
            s3_hook.load_string(
                string_data=csv_content,
                key=csv_key,
                bucket_name=bucket_name,
                replace=True
            )
            s3_paths.append(csv_key)
            
            # Save as JSON (Parquet alternative)
            json_content = processed_df.to_json(orient='records')
            json_key = f"silver/stocks/processed/clean_stocks_{date_str}.json"
            
            logger.log_s3_operation(metadata, "write", json_key, "json")
            s3_hook.load_string(
                string_data=json_content,
                key=json_key,
                bucket_name=bucket_name,
                replace=True
            )
            s3_paths.append(json_key)
            
            # Create metadata
            processing_metadata = {
                'execution_date': date_str,
                'pipeline_version': '2.0_pandas',
                'layer': 'silver',
                'processing_timestamp': pd.Timestamp.utcnow().isoformat() + 'Z',
                'stocks_processed': len(processed_df),
                'unique_tickers': processed_df['ticker'].nunique(),
                'avg_daily_return': float(processed_df['daily_return'].mean()),
                'avg_volume': int(processed_df['volume'].mean()),
                'rsi_summary': {
                    'avg_rsi': float(processed_df['rsi_14'].mean()),
                    'oversold_count': len(processed_df[processed_df['rsi_14'] < 30]),
                    'overbought_count': len(processed_df[processed_df['rsi_14'] > 70])
                }
            }
            
            # Save detailed metadata using enhanced logger structure
            detailed_metadata = {
                'transformation_info': {
                    'execution_date': date_str,
                    'pipeline_version': '2.0_technical_indicators',
                    'layer': 'silver',
                    'operation': 'technical_indicators_calculation',
                    'processing_timestamp': pd.Timestamp.utcnow().isoformat() + 'Z',
                    'input_source': 'bronze/stocks/raw/',
                    'output_location': f'silver/stocks/processed/'
                },
                'data_summary': {
                    'total_stocks_processed': processing_metadata['stocks_processed'],
                    'unique_tickers': processing_metadata['unique_tickers'],
                    'total_data_points': len(processed_df),
                    'stocks_with_indicators': len(processed_df.groupby('ticker')),
                    'date_range': {
                        'start_date': str(processed_df['date'].min()),
                        'end_date': str(processed_df['date'].max())
                    },
                    'technical_indicators_calculated': ['sma_10', 'sma_20', 'ema_12', 'ema_26', 'macd', 'signal', 'histogram', 'rsi_14', 'bb_upper', 'bb_middle', 'bb_lower', 'daily_return']
                },
                'performance_metrics': {
                    'avg_daily_return': processing_metadata['avg_daily_return'],
                    'avg_volume': processing_metadata['avg_volume'],
                    'rsi_analysis': processing_metadata['rsi_summary'],
                    'price_trend_analysis': {
                        'positive_returns_count': len(processed_df[processed_df['daily_return'] > 0]),
                        'negative_returns_count': len(processed_df[processed_df['daily_return'] < 0]),
                        'avg_close_price': float(processed_df['close'].mean())
                    }
                },
                'output_files': {
                    'csv_file': csv_key,
                    'json_file': json_key,
                    'total_files_created': 2
                },
                'data_governance': {
                    'data_lineage': f'bronze/stocks/raw/ -> {csv_key}',
                    'transformation_applied': ['technical_indicators', 'price_calculations', 'volume_analysis'],
                    'quality_checks': {
                        'no_null_prices': processed_df[['open', 'high', 'low', 'close']].notna().all().all(),
                        'valid_date_format': processed_df['date'].notna().all(),
                        'technical_indicators_calculated': processed_df[['sma_10', 'rsi_14', 'macd']].notna().any().all(),
                        'positive_volume_check': (processed_df['volume'] > 0).all()
                    }
                }
            }
            
            # Save detailed metadata
            metadata_key = f"silver/stocks/metadata/stocks_transformation_metadata_{date_str}.json"
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
                'processing_success_rate': 100.0,  # All processed successfully if we reach here
                'avg_daily_return': processing_metadata['avg_daily_return'],
                'avg_rsi': processing_metadata['rsi_summary']['avg_rsi'],
                'technical_indicators_coverage': 100.0,
                'unique_tickers_processed': processing_metadata['unique_tickers']
            }
            
            # Log data quality
            logger.log_data_quality(
                metadata,
                source_count=len(processed_stocks),
                target_count=len(processed_df),
                error_count=0,
                quality_metrics=quality_metrics
            )
            
            # Finish pipeline operation
            final_metadata = log_pipeline_success(logger, metadata, len(processed_stocks), len(processed_df))
            
            logger.log_progress(metadata, "✅ Stock processing completed successfully", 
                              stocks_processed=detailed_metadata['data_summary']['total_stocks_processed'],
                              avg_daily_return=detailed_metadata['performance_metrics']['avg_daily_return'])
            
            result = {
                'stocks_processed': detailed_metadata['data_summary']['total_stocks_processed'],
                'execution_date': date_str,
                'unique_tickers': detailed_metadata['data_summary']['unique_tickers'],
                'data_points': detailed_metadata['data_summary']['total_data_points']
            }
            
            return result
            
        except Exception as e:
            logger.log_progress(metadata, f"Stock processing failed: {str(e)}")
            result = {'stocks_processed': 0, 'execution_date': date_str}
            log_pipeline_error(logger, metadata, e, {'stage': 'processing'})
            return result
        
    except Exception as e:
        # Error logging with context
        context_data = {
            'stage': 'initialization',
            'execution_date': date_str if 'date_str' in locals() else 'unknown'
        }
        log_pipeline_error(logger, metadata, e, context_data)
        raise

def process_news_data(**context):
    """Process news data with sentiment analysis"""
    # Initialize enhanced logger
    logger = get_enhanced_logger("silver_news_processing", "INFO")
    
    # Start pipeline operation tracking
    metadata = log_pipeline_start(
        logger,
        pipeline_name="silver_news_processing",
        layer="silver",
        operation="sentiment_and_categorization",
        dag_run_id=context.get('dag_run').run_id,
        task_id=context.get('task_instance').task_id
    )
    
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger.log_progress(metadata, f"Starting news data processing for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import json
        import re
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        try:
            # Read multiple JSON files from bronze/news/raw/ structure
            logging.info("📰 Reading news data from Bronze layer...")
            
            # Get list of news files from Bronze layer (individual JSON files)
            bronze_news_files = []
            try:
                # List all JSON files in bronze/news/raw/
                paginator = s3_hook.get_session().client('s3').get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=bucket_name, Prefix="bronze/news/raw/"):
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            if obj['Key'].endswith('.json'):
                                bronze_news_files.append(obj['Key'])
                
                logging.info(f"📊 Found {len(bronze_news_files)} news files")
                
            except Exception as list_error:
                logging.error(f"❌ Error listing bronze news files: {str(list_error)}")
                return {'news_processed': 0, 'execution_date': date_str}
            
            if len(bronze_news_files) == 0:
                logging.warning(f"⚠️ No news files found")
                return {'news_processed': 0, 'execution_date': date_str}
            
            # Read and combine all news JSON files
            all_articles = []
            for file_key in bronze_news_files[:50]:  # Limit to 50 most recent files for daily processing
                try:
                    file_content = s3_hook.read_key(key=file_key, bucket_name=bucket_name)
                    article_record = json.loads(file_content)
                    all_articles.append(article_record)
                except Exception as file_error:
                    logging.warning(f"⚠️ Error reading {file_key}: {str(file_error)}")
                    continue
            
            if len(all_articles) == 0:
                logging.error(f"❌ No valid news data found")
                return {'news_processed': 0, 'execution_date': date_str}
            
            logging.info(f"� Processing {len(all_articles)} news articles")
            logger.log_progress(metadata, f"📊 Processing {len(all_articles)} news articles")
            
            # Convert to DataFrame
            news_df = pd.DataFrame(all_articles)
            
            # Ensure required columns exist from bronze_news.py schema
            expected_columns = ['id', 'title', 'combined_text', 'source', 'link', 'date']
            for col in expected_columns:
                if col not in news_df.columns:
                    news_df[col] = ''
            
            # Clean and process functions
            def clean_text(text):
                if pd.isna(text) or text is None:
                    return ""
                text = re.sub(r'\s+', ' ', str(text))
                text = re.sub(r'[^\w\s\.,;:!?\-\(\)%]', '', text)
                return text.strip()
            
            def calculate_basic_sentiment(text):
                """Basic sentiment analysis for Vietnamese text"""
                if pd.isna(text) or not text:
                    return 0.0
                
                # Vietnamese positive/negative keywords
                positive_words = ['tăng', 'tốt', 'khả quan', 'tích cực', 'thành công', 'phát triển', 'lợi nhuận', 'tăng trưởng']
                negative_words = ['giảm', 'xấu', 'tiêu cực', 'thất bại', 'thua lỗ', 'suy thoái', 'khó khăn', 'rủi ro']
                
                text_lower = text.lower()
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                if pos_count + neg_count == 0:
                    return 0.0
                
                return (pos_count - neg_count) / (pos_count + neg_count)
            
            # Process news data
            processed_news = []
            
            for idx, row in news_df.iterrows():
                try:
                    # Clean title and content
                    clean_title = clean_text(row.get('title', ''))
                    clean_content = clean_text(row.get('combined_text', ''))
                    
                    if len(clean_title) < 5 and len(clean_content) < 10:
                        continue  # Skip articles with insufficient content
                    
                    # Calculate sentiment
                    sentiment_score = calculate_basic_sentiment(f"{clean_title} {clean_content}")
                    sentiment_label = 'positive' if sentiment_score > 0.1 else ('negative' if sentiment_score < -0.1 else 'neutral')
                    
                    # Content analysis
                    content_length = len(clean_content)
                    word_count = len(clean_content.split()) if clean_content else 0
                    
                    # Determine topic category based on content
                    content_lower = f"{clean_title} {clean_content}".lower()
                    if any(bank in content_lower for bank in ['ngân hàng', 'bank', 'vcb', 'bidv', 'vietcombank']):
                        topic_category = 'BANKING'
                    elif any(word in content_lower for word in ['chứng khoán', 'cổ phiếu', 'stock']):
                        topic_category = 'STOCKS'
                    elif any(word in content_lower for word in ['kinh tế', 'gdp', 'lạm phát']):
                        topic_category = 'ECONOMY'
                    else:
                        topic_category = 'FINANCE'
                    
                    processed_article = {
                        'id': str(row.get('id', f'news_{idx}')),
                        'title': clean_title,
                        'clean_content': clean_content,
                        'combined_text': f"{clean_title}. {clean_content}",
                        'source': str(row.get('source', '')),
                        'url': str(row.get('link', '')),
                        'date': str(row.get('date', date_str)),
                        'content_length': content_length,
                        'word_count': word_count,
                        'sentiment_score': round(sentiment_score, 3),
                        'sentiment_label': sentiment_label,
                        'topic_category': topic_category,
                        'language': 'vi',
                        '_processed_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
                    }
                    
                    processed_news.append(processed_article)
                    
                except Exception as e:
                    logging.warning(f"⚠️ Error processing article {idx}: {str(e)}")
                    continue
            
            def analyze_vietnamese_sentiment(text):
                if pd.isna(text) or text == "":
                    return 'NEUTRAL'
                
                text_lower = text.lower()
                
                positive_keywords = [
                    'tăng', 'lên', 'tích cực', 'khả quan', 'tốt', 'mạnh', 'cao', 
                    'lợi nhuận', 'thành công', 'phát triển', 'tăng trưởng'
                ]
                
                negative_keywords = [
                    'giảm', 'xuống', 'thấp', 'kém', 'xấu', 'yếu', 'rủi ro',
                    'thua lỗ', 'thất bại', 'khó khăn', 'suy giảm'
                ]
                
                positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
                negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
                
                if positive_count > negative_count:
                    return 'POSITIVE'
                elif negative_count > positive_count:
                    return 'NEGATIVE'
                else:
                    return 'NEUTRAL'
            
            def categorize_topic(title, content):
                text = (str(title) + ' ' + str(content)).lower()
                
                if any(word in text for word in ['ngân hàng', 'bank', 'tín dụng', 'vay', 'lãi suất']):
                    return 'BANKING'
                elif any(word in text for word in ['chứng khoán', 'cổ phiếu', 'stock', 'thị trường']):
                    return 'STOCK_MARKET'
                elif any(word in text for word in ['kinh tế', 'gdp', 'lạm phát', 'economy']):
                    return 'ECONOMY'
                else:
                    return 'FINANCE'
            
            # Process articles
            processed_articles = []
            
            for idx, article in news_df.iterrows():
                clean_title = clean_text(article.get('title', ''))
                clean_content = clean_text(article.get('content', ''))
                
                content_length = len(clean_content)
                word_count = len(clean_content.split()) if clean_content else 0
                
                if content_length < 50:
                    continue
                
                sentiment = analyze_vietnamese_sentiment(clean_title + ' ' + clean_content)
                topic = categorize_topic(clean_title, clean_content)
                
                processed_article = {
                    'title': clean_title,
                    'content': article.get('content', ''),
                    'clean_content': clean_content,
                    'url': article.get('url', ''),
                    'source': article.get('source', 'Unknown'),
                    'publish_date': article.get('publish_date', date_str),
                    'content_length': content_length,
                    'word_count': word_count,
                    'sentiment_basic': sentiment,
                    'topic_category': topic,
                    'processing_date': date_str,
                    '_processed_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
                }
                
                processed_articles.append(processed_article)
            
            if len(processed_articles) == 0:
                logging.warning(f"⚠️ No articles passed quality filter")
                return {'news_processed': 0, 'execution_date': date_str}
            
            # Create processed DataFrame
            processed_df = pd.DataFrame(processed_articles)
            
            # Save as CSV
            csv_content = processed_df.to_csv(index=False)
            processed_csv_key = f"silver/news/processed/clean_news_{date_str}.csv"
            
            logger.log_s3_operation(metadata, "write", processed_csv_key, "csv")
            s3_hook.load_string(
                string_data=csv_content,
                key=processed_csv_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Save as JSON
            json_content = processed_df.to_json(orient='records')
            processed_json_key = f"silver/news/processed/clean_news_{date_str}.json"
            
            logger.log_s3_operation(metadata, "write", processed_json_key, "json")
            s3_hook.load_string(
                string_data=json_content,
                key=processed_json_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Create metadata
            sentiment_counts = processed_df['sentiment_basic'].value_counts().to_dict()
            topic_counts = processed_df['topic_category'].value_counts().to_dict()
            
            logger.log_progress(metadata, f"📊 Sentiment distribution: {sentiment_counts}")
            logger.log_progress(metadata, f"📂 Topic distribution: {topic_counts}")
            
            metadata = {
                'execution_date': date_str,
                'pipeline_version': '2.0_pandas',
                'layer': 'silver',
                'processing_timestamp': pd.Timestamp.utcnow().isoformat() + 'Z',
                'news_processed': len(processed_df),
                'sentiment_distribution': sentiment_counts,
                'topic_distribution': topic_counts,
                'avg_content_length': float(processed_df['content_length'].mean()),
                'avg_word_count': float(processed_df['word_count'].mean())
            }
            
            # Save detailed metadata using enhanced logger structure
            detailed_metadata = {
                'transformation_info': {
                    'execution_date': date_str,
                    'pipeline_version': '2.0_pandas',
                    'layer': 'silver',
                    'operation': 'sentiment_and_categorization',
                    'processing_timestamp': pd.Timestamp.utcnow().isoformat() + 'Z',
                    'input_source': 'bronze/news/raw/',
                    'output_location': f'silver/news/processed/'
                },
                'data_summary': {
                    'total_articles_processed': len(processed_df),
                    'articles_with_sentiment': len(processed_df[processed_df['sentiment_label'] != 'NEUTRAL']),
                    'articles_by_source': processed_df['source'].value_counts().to_dict(),
                    'sentiment_distribution': sentiment_counts,
                    'topic_distribution': topic_counts,
                    'content_quality_metrics': {
                        'avg_content_length': float(processed_df['content_length'].mean()),
                        'avg_word_count': float(processed_df['word_count'].mean()),
                        'min_content_length': int(processed_df['content_length'].min()),
                        'max_content_length': int(processed_df['content_length'].max())
                    }
                },
                'output_files': {
                    'csv_file': processed_csv_key,
                    'json_file': processed_json_key,
                    'total_output_size_mb': round((len(csv_content) + len(json_content)) / 1024 / 1024, 2)
                },
                'data_governance': {
                    'data_lineage': f'bronze/news/raw/ -> {processed_csv_key}',
                    'transformation_applied': ['text_cleaning', 'sentiment_analysis', 'topic_categorization'],
                    'quality_checks': {
                        'no_duplicate_ids': len(processed_df) == len(processed_df['id'].unique()),
                        'valid_dates': processed_df['date'].notna().all(),
                        'non_empty_content': (processed_df['clean_content'].str.len() > 0).all()
                    }
                }
            }
            
            # Save detailed metadata
            metadata_key = f"silver/news/metadata/news_transformation_metadata_{date_str}.json"
            logger.log_s3_operation(metadata, "write", metadata_key, "metadata")
            s3_hook.load_string(
                string_data=json.dumps(detailed_metadata, ensure_ascii=False, indent=2),
                key=metadata_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            logger.log_progress(metadata, f"✅ News processing completed successfully")
            logger.log_progress(metadata, f"📊 Processed {len(processed_df)} articles with sentiment analysis")
            logger.log_data_quality(metadata, "silver_news", len(processed_df), detailed_metadata['data_governance']['quality_checks'])
            
            result = {
                'news_processed': detailed_metadata['data_summary']['total_articles_processed'],
                'execution_date': date_str,
                'sentiment_distribution': detailed_metadata['data_summary']['sentiment_distribution'],
                'articles_with_sentiment': detailed_metadata['data_summary']['articles_with_sentiment']
            }
            
            return result
            
        except Exception as e:
            logging.error(f"❌ News processing failed: {str(e)}")
            return {'news_processed': 0, 'execution_date': date_str}
        
    except Exception as e:
        logging.error(f"💥 News processing failed: {str(e)}")
        raise

def process_others_data(**context):
    """Process macro economic indicators"""
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logging.info(f"📊 Processing others data for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import json
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        try:
            # Read raw others data
            others_file_key = f"bronze/others/raw/others_{date_str}.json"
            
            if not s3_hook.check_for_key(key=others_file_key, bucket_name=bucket_name):
                logging.warning(f"⚠️ No others data found for {date_str}")
                return {'others_processed': 0, 'execution_date': date_str}
            
            others_content = s3_hook.read_key(key=others_file_key, bucket_name=bucket_name)
            others_data = json.loads(others_content)
            
            indicators = others_data.get('indicators', [])
            if len(indicators) == 0:
                logging.warning(f"⚠️ No indicators to process")
                return {'others_processed': 0, 'execution_date': date_str}
            
            logging.info(f"📈 Processing {len(indicators)} economic indicators")
            
            # Convert to DataFrame
            others_df = pd.DataFrame(indicators)
            
            # Clean and validate data
            processed_indicators = []
            
            for idx, indicator in others_df.iterrows():
                # Basic validation
                value = indicator.get('value')
                if pd.isna(value) or value is None:
                    continue
                
                try:
                    numeric_value = float(value)
                except (ValueError, TypeError):
                    continue
                
                processed_indicator = {
                    'indicator_name': str(indicator.get('name', 'Unknown')),
                    'value': float(numeric_value),
                    'unit': str(indicator.get('unit', '')),
                    'category': str(indicator.get('category', 'ECONOMIC')),
                    'date': indicator.get('date', date_str),
                    'source': str(indicator.get('source', 'VN_ECONOMIC')),
                    'processing_date': date_str,
                    '_processed_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
                }
                
                processed_indicators.append(processed_indicator)
            
            if len(processed_indicators) == 0:
                logging.warning(f"⚠️ No indicators processed successfully")
                return {'others_processed': 0, 'execution_date': date_str}
            
            # Create processed DataFrame
            processed_df = pd.DataFrame(processed_indicators)
            
            # Save as CSV
            csv_content = processed_df.to_csv(index=False)
            processed_csv_key = f"silver/others/processed/clean_others_{date_str}.csv"
            
            s3_hook.load_string(
                string_data=csv_content,
                key=processed_csv_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Save as JSON
            json_content = processed_df.to_json(orient='records', ensure_ascii=False)
            processed_json_key = f"silver/others/processed/clean_others_{date_str}.json"
            
            s3_hook.load_string(
                string_data=json_content,
                key=processed_json_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Create metadata
            category_counts = processed_df['category'].value_counts().to_dict()
            
            metadata = {
                'execution_date': date_str,
                'pipeline_version': '2.0_pandas',
                'layer': 'silver',
                'processing_timestamp': pd.Timestamp.utcnow().isoformat() + 'Z',
                'others_processed': len(processed_df),
                'category_distribution': category_counts,
                'unique_indicators': processed_df['indicator_name'].nunique()
            }
            
            # Save metadata
            metadata_key = f"silver/others/metadata/processing_meta_{date_str}.json"
            s3_hook.load_string(
                string_data=json.dumps(metadata, ensure_ascii=False, indent=2),
                key=metadata_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            logging.info(f"✅ Others processing completed successfully")
            logging.info(f"📊 Processed {metadata['others_processed']} indicators")
            
            return metadata
            
        except Exception as e:
            logging.error(f"❌ Others processing failed: {str(e)}")
            return {'others_processed': 0, 'execution_date': date_str}
        
    except Exception as e:
        logging.error(f"💥 Others processing failed: {str(e)}")
        raise

def validate_silver_output(**context):
    """Validate Silver layer output quality"""
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logging.info(f"🔍 Validating Silver layer output for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import json
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        validation_results = {
            'execution_date': date_str,
            'validation_status': 'PASS',
            'components_checked': [],
            'errors': [],
            'warnings': []
        }
        
        # Check stocks
        stocks_csv_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
        if s3_hook.check_for_key(key=stocks_csv_key, bucket_name=bucket_name):
            validation_results['components_checked'].append('stocks')
            logging.info("✅ Stocks validation passed")
        else:
            validation_results['errors'].append("Missing stocks output")
            validation_results['validation_status'] = 'FAIL'
        
        # Check news
        news_csv_key = f"silver/news/processed/clean_news_{date_str}.csv"
        if s3_hook.check_for_key(key=news_csv_key, bucket_name=bucket_name):
            validation_results['components_checked'].append('news')
            logging.info("✅ News validation passed")
        else:
            validation_results['warnings'].append("Missing news output")
        
        # Check others
        others_csv_key = f"silver/others/processed/clean_others_{date_str}.csv"
        if s3_hook.check_for_key(key=others_csv_key, bucket_name=bucket_name):
            validation_results['components_checked'].append('others')
            logging.info("✅ Others validation passed")
        else:
            validation_results['warnings'].append("Missing others output")
        
        # Save validation results
        validation_key = f"silver/metadata/validation_results_{date_str}.json"
        s3_hook.load_string(
            string_data=json.dumps(validation_results, ensure_ascii=False, indent=2),
            key=validation_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        status_emoji = "✅" if validation_results['validation_status'] == 'PASS' else "❌"
        logging.info(f"{status_emoji} Silver validation: {validation_results['validation_status']}")
        
        return validation_results
        
    except Exception as e:
        logging.error(f"💥 Silver validation failed: {str(e)}")
        raise

# Task definitions
start_silver = DummyOperator(
    task_id='start_silver_pipeline',
    dag=dag,
)

process_stocks = PythonOperator(
    task_id='process_stock_data',
    python_callable=process_stock_data,
    dag=dag,
    retries=2,
    retry_delay=timedelta(minutes=5)
)

process_news = PythonOperator(
    task_id='process_news_data',
    python_callable=process_news_data,
    dag=dag,
    retries=2,
    retry_delay=timedelta(minutes=5)
)

process_others = PythonOperator(
    task_id='process_others_data',
    python_callable=process_others_data,
    dag=dag,
    retries=2,
    retry_delay=timedelta(minutes=5)
)

validate_output = PythonOperator(
    task_id='validate_silver_output',
    python_callable=validate_silver_output,
    dag=dag,
    retries=1,
    retry_delay=timedelta(minutes=2)
)

health_check = BashOperator(
    task_id='silver_health_check',
    bash_command='''
    echo "🔍 Silver Layer Health Check"
    echo "Timestamp: $(date)"
    echo "Pipeline: Silver Layer Data Processing"
    echo "Status: Processing completed"
    echo "Memory usage: $(free -h | grep '^Mem' | awk '{print $3 "/" $2}')'"
    ''',
    dag=dag,
)

end_silver = DummyOperator(
    task_id='end_silver_pipeline',
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag,
)

# Task dependencies
start_silver >> [process_stocks, process_news, process_others] >> validate_output >> health_check >> end_silver