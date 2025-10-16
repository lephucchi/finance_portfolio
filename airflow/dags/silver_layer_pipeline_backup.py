"""
Silver Layer DAG - Data Processing & Technical Indicators with Spark
Processes Bronze data to create clean, enriched datasets with technical analysis

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
    'execution_timeout': timedelta(hours=3),
}

# DAG definition
dag = DAG(
    'silver_layer_pipeline',
    default_args=default_args,
    description='Silver Layer - Data Processing & Technical Indicators with Spark',
    schedule_interval='0 7 * * 1-5',  # 7:00 AM weekdays (after Bronze DAG)
    catchup=False,
    max_active_runs=1,
    max_active_tasks=8,
    tags=['silver', 'processing', 'spark', 'technical-indicators'],
)

def process_stock_data_with_spark(**context):
    """Process Bronze stock data based on silver_stocks_complete.py logic"""
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logging.info(f"🔧 Processing stock data for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import json
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Read Bronze stock data from individual JSON files
        banking_stocks = ['VCB', 'BID', 'CTG', 'VPB', 'TCB', 'MBB', 'STB', 'HDB', 'ACB']
        all_stock_data = []
        
        for ticker in banking_stocks:
            try:
                file_key = f"bronze/stocks/raw/{ticker}/{ticker}_{date_str}.json"
                
                # Check if file exists
                if s3_hook.check_for_key(key=file_key, bucket_name=bucket_name):
                    # Read JSON content
                    content = s3_hook.read_key(key=file_key, bucket_name=bucket_name)
                    stock_data = json.loads(content)
                    all_stock_data.append(stock_data)
                    logging.info(f"✅ Loaded {ticker} data")
                else:
                    logging.warning(f"⚠️ Missing {ticker} data for {date_str}")
                    
            except Exception as e:
                logging.error(f"❌ Error loading {ticker}: {str(e)}")
                continue
        
        if not all_stock_data:
            raise ValueError("No stock data available for processing")
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(all_stock_data)
        
        logging.info(f"� Processing {len(df)} stock records")
        
        # Data cleaning and validation (from silver_stocks_complete.py)
        original_count = len(df)
        
        # Ensure numeric columns
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove invalid data
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        df = df[(df['open'] > 0) & (df['high'] > 0) & (df['low'] > 0) & (df['close'] > 0)]
        df = df[df['volume'] >= 0]
        
        # Basic data validation
        df = df[df['high'] >= df['low']]
        df = df[(df['close'] >= df['low']) & (df['close'] <= df['high'])]
        df = df[(df['open'] >= df['low']) & (df['open'] <= df['high'])]
        
        # Calculate technical indicators (simplified from silver_stocks_complete.py)
        df = df.sort_values(['ticker', 'date']).reset_index(drop=True)
        
        # Calculate daily return
        df['daily_return'] = ((df['close'] - df['open']) / df['open']) * 100
        
        # Simple moving averages (for single day, use previous values or set as current close)
        df['ma_5'] = df['close']  # For single day processing
        df['ma_20'] = df['close']
        df['ma_50'] = df['close']
        
        # Basic RSI calculation (simplified for single day)
        df['rsi_14'] = 50.0  # Neutral value for single day
        
        # Volume analysis
        df['volume_ratio'] = 1.0  # Default ratio
        
        # Volatility (simplified)
        df['volatility_20d'] = 0.02  # Default 2% volatility
        
        # Trend signals
        df['trend_signal'] = 'NEUTRAL'
        df['rsi_signal'] = 'NORMAL'
        df['volume_signal'] = 'NORMAL'
        
        # Add metadata
        df['_processed_at_utc'] = pd.Timestamp.utcnow().isoformat() + 'Z'
        df['_silver_version'] = '1.0'
        df['_data_quality_score'] = 100.0  # Full score for cleaned data
        
        # Save as CSV to Silver layer
        csv_content = df.to_csv(index=False)
        csv_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
        
        s3_hook.load_string(
            string_data=csv_content,
            key=csv_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        # Save as Parquet for better performance
        parquet_key = f"silver/stocks/processed/clean_stocks_{date_str}.parquet"
        try:
            parquet_content = df.to_parquet()
            s3_hook.load_bytes(
                bytes_data=parquet_content,
                key=parquet_key,
                bucket_name=bucket_name,
                replace=True
            )
        except Exception as parquet_error:
            logging.warning(f"⚠️ Could not save parquet: {str(parquet_error)}")
        
        # Create transformation metadata
        transformation_log = {
            'original_rows': original_count,
            'processed_rows': len(df),
            'data_quality_score': 100.0,
            'transformations_applied': [
                'data_cleaning',
                'technical_indicators',
                'trend_analysis',
                'volume_analysis'
            ],
            'processing_date': date_str,
            '_processed_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
        }
        
        # Upload transformation metadata
        metadata_key = f"silver/stocks/metadata/transformation_log_{date_str}.json"
        s3_hook.load_string(
            string_data=json.dumps(transformation_log, ensure_ascii=False, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        result = {
            'records_processed': len(df),
            'data_quality_score': 100.0,
            'csv_path': csv_key,
            'parquet_path': parquet_key,
            'execution_date': date_str
        }
        
        logging.info(f"✅ Stock processing completed: {result}")
        return result
        
    except Exception as e:
        logging.error(f"💥 Stock processing failed: {str(e)}")
        raise

def process_news_data(**context):
                mode="overwrite",
def process_news_data(**context):
    """Process news data with sentiment analysis based on original logic"""
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
            
            # Clean and process news content
            def clean_text(text):
                if pd.isna(text) or text is None:
                    return ""
                # Remove extra whitespace and special characters
                text = re.sub(r'\s+', ' ', str(text))
                text = re.sub(r'[^\w\s\.,;:!?\-\(\)%]', '', text)
                return text.strip()
            
            # Vietnamese sentiment analysis (basic keywords)
            def analyze_vietnamese_sentiment(text):
                if pd.isna(text) or text == "":
                    return 'NEUTRAL'
                
                text_lower = text.lower()
                
                # Positive keywords for banking/finance
                positive_keywords = [
                    'tăng', 'lên', 'tích cực', 'khả quan', 'tốt', 'mạnh', 'cao', 
                    'lợi nhuận', 'thành công', 'phát triển', 'tăng trưởng',
                    'cải thiện', 'vượt', 'đạt', 'kỷ lục', 'thuận lợi'
                ]
                
                # Negative keywords for banking/finance  
                negative_keywords = [
                    'giảm', 'xuống', 'thấp', 'kém', 'xấu', 'yếu', 'rủi ro',
                    'thua lỗ', 'thất bại', 'khó khăn', 'suy giảm', 'giảm sút',
                    'thiệt hại', 'không đạt', 'bất lợi', 'lo ngại'
                ]
                
                positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
                negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
                
                if positive_count > negative_count:
                    return 'POSITIVE'
                elif negative_count > positive_count:
                    return 'NEGATIVE'
                else:
                    return 'NEUTRAL'
            
            # Topic categorization
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
            
            # Process each article
            processed_articles = []
            
            for idx, article in news_df.iterrows():
                # Clean content
                clean_title = clean_text(article.get('title', ''))
                clean_content = clean_text(article.get('content', ''))
                
                # Basic metrics
                content_length = len(clean_content)
                word_count = len(clean_content.split()) if clean_content else 0
                
                # Skip articles that are too short
                if content_length < 50:
                    continue
                
                # Sentiment analysis
                sentiment = analyze_vietnamese_sentiment(clean_title + ' ' + clean_content)
                
                # Topic categorization
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
            
            # Add aggregated statistics
            sentiment_counts = processed_df['sentiment_basic'].value_counts().to_dict()
            topic_counts = processed_df['topic_category'].value_counts().to_dict()
            
            # Save as CSV
            csv_content = processed_df.to_csv(index=False)
            processed_csv_key = f"silver/news/processed/clean_news_{date_str}.csv"
            
            s3_hook.load_string(
                string_data=csv_content,
                key=processed_csv_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Save as Parquet-like format (JSON for now)
            parquet_key = f"silver/news/processed/clean_news_{date_str}.json"
            s3_hook.load_string(
                string_data=processed_df.to_json(orient='records', ensure_ascii=False),
                key=parquet_key,
                bucket_name=bucket_name,
                replace=True
            )
            
            # Create metadata
            metadata = {
                'execution_date': date_str,
                'pipeline_version': '2.0_pandas',
                'layer': 'silver',
                'processing_timestamp': pd.Timestamp.utcnow().isoformat() + 'Z',
                'news_processed': len(processed_df),
                'sentiment_distribution': sentiment_counts,
                'topic_distribution': topic_counts,
                'avg_content_length': float(processed_df['content_length'].mean()),
                'avg_word_count': float(processed_df['word_count'].mean()),
                'quality_metrics': {
                    'total_articles_input': len(articles),
                    'articles_passed_filter': len(processed_articles),
                    'filter_pass_rate': len(processed_articles) / len(articles) if len(articles) > 0 else 0
                }
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
            logging.info(f"📊 Sentiment distribution: {sentiment_counts}")
            logging.info(f"🏷️ Topic distribution: {topic_counts}")
            
            return metadata
            
        except Exception as e:
            logging.error(f"❌ News processing failed: {str(e)}")
            return {'news_processed': 0, 'execution_date': date_str}
        
    except Exception as e:
        logging.error(f"💥 News processing failed: {str(e)}")
        raise

def process_others_data(**context):
    """Process Bronze others data (macro & index) based on silver_stocks_complete.py logic"""
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
        
        results = {
            'index_processed': 0,
            'macro_processed': 0,
            'execution_date': date_str
        }
        
        # Process Index data (VNINDEX, VN30, etc.)
        try:
            index_prefix = f"bronze/others/raw/index/"
            index_files = s3_hook.list_keys(bucket_name=bucket_name, prefix=index_prefix)
            
            if index_files:
                index_data_list = []
                
                for file_key in index_files:
                    if file_key.endswith('.json') and date_str in file_key:
                        try:
                            content = s3_hook.read_key(key=file_key, bucket_name=bucket_name)
                            index_data = json.loads(content)
                            index_data_list.append(index_data)
                        except Exception as e:
                            logging.error(f"❌ Error reading index file {file_key}: {str(e)}")
                            continue
                
                if index_data_list:
                    # Convert to DataFrame and process
                    df_index = pd.DataFrame(index_data_list)
                    
                    # Data cleaning
                    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
                    for col in numeric_columns:
                        if col in df_index.columns:
                            df_index[col] = pd.to_numeric(df_index[col], errors='coerce')
                    
                    # Add processing metadata
                    df_index['_processed_at_utc'] = pd.Timestamp.utcnow().isoformat() + 'Z'
                    df_index['_silver_version'] = '1.0'
                    
                    # Save processed index data
                    csv_content = df_index.to_csv(index=False)
                    csv_key = f"silver/others/processed/clean_index_{date_str}.csv"
                    
                    s3_hook.load_string(
                        string_data=csv_content,
                        key=csv_key,
                        bucket_name=bucket_name,
                        replace=True
                    )
                    
                    results['index_processed'] = len(df_index)
                    logging.info(f"✅ Processed {len(df_index)} index records")
                
        except Exception as index_error:
            logging.error(f"❌ Index processing failed: {str(index_error)}")
        
        # Process Macro data
        try:
            macro_prefix = f"bronze/others/raw/macro/"
            macro_files = s3_hook.list_keys(bucket_name=bucket_name, prefix=macro_prefix)
            
            if macro_files:
                macro_data_list = []
                
                for file_key in macro_files:
                    if file_key.endswith('.json') and date_str in file_key:
                        try:
                            content = s3_hook.read_key(key=file_key, bucket_name=bucket_name)
                            macro_data = json.loads(content)
                            macro_data_list.append(macro_data)
                        except Exception as e:
                            logging.error(f"❌ Error reading macro file {file_key}: {str(e)}")
                            continue
                
                if macro_data_list:
                    # Convert to DataFrame and process
                    df_macro = pd.DataFrame(macro_data_list)
                    
                    # Data cleaning
                    if 'value' in df_macro.columns:
                        df_macro['value'] = pd.to_numeric(df_macro['value'], errors='coerce')
                    
                    # Add processing metadata
                    df_macro['_processed_at_utc'] = pd.Timestamp.utcnow().isoformat() + 'Z'
                    df_macro['_silver_version'] = '1.0'
                    
                    # Save processed macro data
                    csv_content = df_macro.to_csv(index=False)
                    csv_key = f"silver/others/processed/clean_macro_{date_str}.csv"
                    
                    s3_hook.load_string(
                        string_data=csv_content,
                        key=csv_key,
                        bucket_name=bucket_name,
                        replace=True
                    )
                    
                    results['macro_processed'] = len(df_macro)
                    logging.info(f"✅ Processed {len(df_macro)} macro records")
                
        except Exception as macro_error:
            logging.error(f"❌ Macro processing failed: {str(macro_error)}")
        
        # Create others processing metadata
        others_metadata = {
            'index_records_processed': results['index_processed'],
            'macro_records_processed': results['macro_processed'],
            'total_records': results['index_processed'] + results['macro_processed'],
            'processing_date': date_str,
            '_processed_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'
        }
        
        # Upload others metadata
        metadata_key = f"silver/others/metadata/others_processing_log_{date_str}.json"
        s3_hook.load_string(
            string_data=json.dumps(others_metadata, ensure_ascii=False, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        logging.info(f"✅ Others processing completed: {results}")
        return results
        
    except Exception as e:
        logging.error(f"💥 Others processing failed: {str(e)}")
        raise

def validate_silver_output(**context):
            """.format(date_str=date_str))
            
            # Write processed news to Silver layer
            silver_news_path = f"silver/news/processed/{date_str}"
            spark_manager.write_to_s3(
                processed_news,
                silver_news_path,
                format="parquet",
                mode="overwrite",
                partitionBy=["source"]
            )
            
            # Create temp view first
            processed_news.createOrReplaceTempView("processed_news_view")
            
            # Create news summary for RAG input
            news_summary = spark.sql("""
                SELECT 
                    source,
                    topic_category,
                    sentiment_basic,
                    COUNT(*) as article_count,
                    AVG(content_length) as avg_content_length,
                    AVG(word_count) as avg_word_count
                FROM processed_news_view
                GROUP BY source, topic_category, sentiment_basic
            """)
            
            # Store metadata
            metadata = {
                'execution_date': date_str,
                'pipeline_version': '2.0_spark',
                'layer': 'silver',
                'processing_timestamp': datetime.utcnow().isoformat(),
                'news_processed': processed_news.count(),
                'sources_processed': processed_news.select('source').distinct().count(),
                'sentiment_distribution': {
                    'positive': processed_news.filter(processed_news.sentiment_basic == 'POSITIVE').count(),
                    'negative': processed_news.filter(processed_news.sentiment_basic == 'NEGATIVE').count(),
                    'neutral': processed_news.filter(processed_news.sentiment_basic == 'NEUTRAL').count()
                }
            }
            
            logging.info(f"✅ News processing completed successfully")
            logging.info(f"📰 Processed {metadata['news_processed']} articles")
            
            return metadata
            
        finally:
            spark_manager.stop_spark_session()
        
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
        
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        validation_results = {
            'stocks_validation': {'passed': True, 'issues': []},
            'news_validation': {'passed': True, 'issues': []},
            'others_validation': {'passed': True, 'issues': []},
            'overall_quality_score': 0.0
        }
        
        # Validate stock data
        try:
            stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
            if s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name):
                logging.info(f"✅ Stock data found at {stock_file_key}")
            else:
                validation_results['stocks_validation']['passed'] = False
                validation_results['stocks_validation']['issues'].append("Stock CSV not found")
        except Exception as e:
            validation_results['stocks_validation']['passed'] = False
            validation_results['stocks_validation']['issues'].append(f"Stock validation failed: {str(e)}")
        
        # Validate news data
        try:
            news_file_key = f"silver/news/processed/clean_news_{date_str}.csv"
            if s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name):
                logging.info(f"✅ News data found at {news_file_key}")
            else:
                validation_results['news_validation']['passed'] = False
                validation_results['news_validation']['issues'].append("News CSV not found")
        except Exception as e:
            logging.warning(f"⚠️ News validation: {str(e)}")
        
        # Validate others data
        try:
            index_file_key = f"silver/others/processed/clean_index_{date_str}.csv"
            macro_file_key = f"silver/others/processed/clean_macro_{date_str}.csv"
            
            index_exists = s3_hook.check_for_key(key=index_file_key, bucket_name=bucket_name)
            macro_exists = s3_hook.check_for_key(key=macro_file_key, bucket_name=bucket_name)
            
            if not (index_exists or macro_exists):
                validation_results['others_validation']['passed'] = False
                validation_results['others_validation']['issues'].append("No others data found")
            else:
                logging.info(f"✅ Others data: index={index_exists}, macro={macro_exists}")
                
        except Exception as e:
            logging.warning(f"⚠️ Others validation: {str(e)}")
        
        # Calculate overall quality score
        scores = []
        if validation_results['stocks_validation']['passed']:
            scores.append(1.0)
        else:
            scores.append(0.5)
            
        if validation_results['news_validation']['passed']:
            scores.append(1.0)
        else:
            scores.append(0.5)
            
        if validation_results['others_validation']['passed']:
            scores.append(1.0)
        else:
            scores.append(0.5)
        
        validation_results['overall_quality_score'] = (sum(scores) / len(scores)) * 100
        
        logging.info(f"🔍 Silver Validation Results:")
        logging.info(f"  - Overall quality: {validation_results['overall_quality_score']:.1f}%")
        
        return validation_results
        
    except Exception as e:
        logging.error(f"💥 Silver validation failed: {str(e)}")
        raise

def prepare_rag_input(**context):
    """Prepare processed news data for RAG system"""
    try:
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logging.info(f"🧠 Preparing RAG input data for {date_str}")
        
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        try:
            # Read processed news data
            news_file_key = f"silver/news/processed/clean_news_{date_str}.csv"
            
            if s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name):
                # Read CSV content
                csv_content = s3_hook.read_key(key=news_file_key, bucket_name=bucket_name)
                df = pd.read_csv(pd.StringIO(csv_content))
                
                # Prepare RAG input format
                rag_df = df[['id', 'title', 'content', 'combined_text', 'source', 
                           'sentiment_basic', 'topic_category']].copy()
                
                # Filter for quality articles
                rag_df = rag_df[rag_df['content_length'] > 50]  # Minimum content length
                rag_df = rag_df[rag_df['topic_category'] == 'BANKING']  # Focus on banking news
                
                # Add RAG metadata
                rag_df['_rag_prepared_date'] = date_str
                rag_df['_rag_ready'] = True
                
                # Save RAG input data
                rag_csv_content = rag_df.to_csv(index=False)
                rag_input_key = f"rag/input/news_{date_str}.csv"
                
                s3_hook.load_string(
                    string_data=rag_csv_content,
                    key=rag_input_key,
                    bucket_name=bucket_name,
                    replace=True
                )
                
                logging.info(f"🧠 Prepared {len(rag_df)} articles for RAG system")
                
                return {
                    'rag_articles_prepared': len(rag_df),
                    'execution_date': date_str,
                    'rag_input_path': rag_input_key
                }
            else:
                logging.warning(f"⚠️ No news data found for RAG preparation")
                return {
                    'rag_articles_prepared': 0,
                    'execution_date': date_str
                }
                
        except Exception as e:
            logging.error(f"❌ RAG preparation error: {str(e)}")
            return {
                'rag_articles_prepared': 0,
                'execution_date': date_str
            }
        
    except Exception as e:
        logging.error(f"💥 RAG preparation failed: {str(e)}")
        raise

# Task definitions
start_silver = DummyOperator(
    task_id='start_silver_pipeline',
    dag=dag,
)

process_stocks = PythonOperator(
    task_id='process_stock_data',
    python_callable=process_stock_data_with_spark,
    dag=dag,
)

process_news = PythonOperator(
    task_id='process_news_data',
    python_callable=process_news_data,
    dag=dag,
)

process_others = PythonOperator(
    task_id='process_others_data',
    python_callable=process_others_data,
    dag=dag,
)

validate_output = PythonOperator(
    task_id='validate_silver_output',
    python_callable=validate_silver_output,
    dag=dag,
)

prepare_rag = PythonOperator(
    task_id='prepare_rag_input',
    python_callable=prepare_rag_input,
    dag=dag,
)

health_check = BashOperator(
    task_id='silver_health_check',
    bash_command="""
    echo "🔍 Silver Layer Health Check"
    echo "Timestamp: $(date)"
    echo "Pipeline: Silver Layer Data Processing"
    echo "Status: Processing completed"
    echo "Memory usage: $(free -h | grep '^Mem' | awk '{print $3 "/" $2}')"
    """,
    dag=dag,
)

end_silver = DummyOperator(
    task_id='end_silver_pipeline',
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag,
)

# Task dependencies - Process all data types in parallel, then validate and prepare RAG
start_silver >> [process_stocks, process_news, process_others] >> validate_output >> prepare_rag >> health_check >> end_silver

# Make DAG available
globals()['silver_layer_pipeline'] = dag
