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
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logging.info(f"📈 Processing stock data for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import numpy as np
        import json
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        try:
            # Read raw stock data
            stock_file_key = f"bronze/stocks/raw/stocks_{date_str}.json"
            
            if not s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name):
                logging.warning(f"⚠️ No stock data found for {date_str}")
                return {'stocks_processed': 0, 'execution_date': date_str}
            
            stock_content = s3_hook.read_key(key=stock_file_key, bucket_name=bucket_name)
            stock_data = json.loads(stock_content)
            
            stocks = stock_data.get('stocks', [])
            if len(stocks) == 0:
                logging.warning(f"⚠️ No stocks to process")
                return {'stocks_processed': 0, 'execution_date': date_str}
            
            logging.info(f"💹 Processing {len(stocks)} stock records")
            
            # Convert to DataFrame
            stocks_df = pd.DataFrame(stocks)
            
            # Ensure numeric columns
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                if col in stocks_df.columns:
                    stocks_df[col] = pd.to_numeric(stocks_df[col], errors='coerce')
            
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
                logging.warning(f"⚠️ No stocks processed successfully")
                return {'stocks_processed': 0, 'execution_date': date_str}
            
            # Create processed DataFrame
            processed_df = pd.DataFrame(processed_stocks)
            
            # Save as CSV
            csv_content = processed_df.to_csv(index=False)
            processed_csv_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
            
            s3_hook.load_string(
                string_data=csv_content,
                key=processed_csv_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Save as JSON (Parquet alternative)
            json_content = processed_df.to_json(orient='records', ensure_ascii=False)
            processed_json_key = f"silver/stocks/processed/clean_stocks_{date_str}.json"
            
            s3_hook.load_string(
                string_data=json_content,
                key=processed_json_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Create metadata
            metadata = {
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
            
            # Save metadata
            metadata_key = f"silver/stocks/metadata/processing_meta_{date_str}.json"
            s3_hook.load_string(
                string_data=json.dumps(metadata, ensure_ascii=False, indent=2),
                key=metadata_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            logging.info(f"✅ Stock processing completed successfully")
            logging.info(f"📊 Processed {metadata['stocks_processed']} stocks")
            logging.info(f"📈 Average daily return: {metadata['avg_daily_return']:.4f}")
            
            return metadata
            
        except Exception as e:
            logging.error(f"❌ Stock processing failed: {str(e)}")
            return {'stocks_processed': 0, 'execution_date': date_str}
        
    except Exception as e:
        logging.error(f"💥 Stock processing failed: {str(e)}")
        raise

def process_news_data(**context):
    """Process news data with sentiment analysis"""
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logging.info(f"📰 Processing news data for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import json
        import re
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        try:
            # Read raw news data
            news_file_key = f"bronze/news/raw/news_{date_str}.json"
            
            if not s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name):
                logging.warning(f"⚠️ No news data found for {date_str}")
                return {'news_processed': 0, 'execution_date': date_str}
            
            news_content = s3_hook.read_key(key=news_file_key, bucket_name=bucket_name)
            news_data = json.loads(news_content)
            
            articles = news_data.get('articles', [])
            if len(articles) == 0:
                logging.warning(f"⚠️ No articles to process")
                return {'news_processed': 0, 'execution_date': date_str}
            
            logging.info(f"📄 Processing {len(articles)} news articles")
            
            # Convert to DataFrame
            news_df = pd.DataFrame(articles)
            
            # Clean and process functions
            def clean_text(text):
                if pd.isna(text) or text is None:
                    return ""
                text = re.sub(r'\s+', ' ', str(text))
                text = re.sub(r'[^\w\s\.,;:!?\-\(\)%]', '', text)
                return text.strip()
            
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
            
            s3_hook.load_string(
                string_data=csv_content,
                key=processed_csv_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Save as JSON
            json_content = processed_df.to_json(orient='records', ensure_ascii=False)
            processed_json_key = f"silver/news/processed/clean_news_{date_str}.json"
            
            s3_hook.load_string(
                string_data=json_content,
                key=processed_json_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Create metadata
            sentiment_counts = processed_df['sentiment_basic'].value_counts().to_dict()
            topic_counts = processed_df['topic_category'].value_counts().to_dict()
            
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
            
            # Save metadata
            metadata_key = f"silver/news/metadata/processing_meta_{date_str}.json"
            s3_hook.load_string(
                string_data=json.dumps(metadata, ensure_ascii=False, indent=2),
                key=metadata_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            logging.info(f"✅ News processing completed successfully")
            logging.info(f"📰 Processed {metadata['news_processed']} articles")
            
            return metadata
            
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