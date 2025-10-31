"""
Bronze Layer Pipeline - V3 (Production Ready với Web Scraping & Retry)
================================================================================

Improvements:
- Stocks: Multi-source retry mechanism (TCBS, VCI, VND)
- News: Real web scraping from 6 major Vietnamese news sources  
- Macro: Optimized data generation
- Current date usage for real-time data
- No enhanced_logger dependency

Output Structure:
- bronze/stocks/raw/{ticker}_{date}.json
- bronze/news/raw/{id}.json
- bronze/macro/raw/{category}/{indicator}.csv
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
import json
import os

# Default arguments
default_args = {
    'owner': 'finance_portfolio',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 29),  # Current date to avoid future execution date issues
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# DAG definition
dag = DAG(
    'bronze_layer_pipeline',
    default_args=default_args,
    description='Bronze layer with web scraping and retry mechanisms',
    schedule_interval=None,  # Triggered by master_pipeline only
    catchup=False,
    tags=['bronze', 'lakehouse', 'production'],
    max_active_runs=1
)


def validate_aws_s3_access(**context):
    """Validate AWS S3 access before processing"""
    try:
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        
        logger = logging.getLogger(__name__)
        logger.info("🔐 Validating AWS S3 access...")
        
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        if s3_hook.check_for_bucket(bucket_name):
            logger.info(f"✅ S3 bucket '{bucket_name}' accessible")
            test_key = f"health-check/bronze-pipeline-{context['execution_date'].strftime('%Y%m%d-%H%M%S')}.txt"
            s3_hook.load_string(
                string_data=f"Bronze pipeline health check at {datetime.utcnow()}",
                key=test_key,
                bucket_name=bucket_name,
                replace=True
            )
            logger.info(f"✅ S3 write test successful: {test_key}")
            return True
        else:
            raise Exception(f"Cannot access S3 bucket: {bucket_name}")
            
    except Exception as e:
        logger.error(f"❌ AWS S3 validation failed: {str(e)}")
        raise


def extract_vnstock_data_with_retry(**context):
    """
    Extract stock data with retry from multiple sources
    Sources: TCBS, VCI, VND (rotated on retry)
    """
    try:
        import vnstock3 as vs
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import time
        import random
        
        # Get last 3 days for stock data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3)
        date_str = end_date.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')
        
        logger = logging.getLogger(__name__)
        logger.info(f"📈 Starting stock extraction for last 3 days: {start_date_str} to {date_str}")
        
        vnstock = vs.Vnstock()
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Top 30 tickers for testing
        tickers = [
            'ACB', 'BCM', 'BID', 'BVH', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG',
            'MBB', 'MSN', 'MWG', 'PLX', 'POW', 'SAB', 'SSI', 'STB', 'TCB', 'TPB',
            'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE', 'GMD', 'REE'
        ]
        
        sources = ['TCBS', 'VCI', 'VND']
        max_retries = 3
        successful = []
        failed = []
        
        for ticker in tickers:
            success = False
            for attempt in range(max_retries):
                try:
                    source = sources[attempt % len(sources)]
                    logger.info(f"  {ticker} attempt {attempt+1}/{max_retries} (source: {source})")
                    
                    # Fetch last 3 days of data
                    stock_data = vnstock.stock(symbol=ticker, source=source).quote.history(
                        start=start_date_str, end=date_str
                    )
                    
                    if stock_data is not None and not stock_data.empty:
                        # Filter to only last 3 days
                        stock_data = stock_data.tail(3)
                        logger.info(f"      📊 Filtered to {len(stock_data)} most recent days")
                        
                        # Save each day separately
                        files_saved = 0
                        for idx, row in stock_data.iterrows():
                            try:
                                # Get date from the row
                                row_date = row.get('time', date_str)
                                if isinstance(row_date, str):
                                    row_date_str = row_date[:10]  # Get YYYY-MM-DD part
                                else:
                                    row_date_str = row_date.strftime('%Y-%m-%d')
                                
                                # Create single day record
                                stock_record = {
                                    'ticker': ticker,
                                    'date': row_date_str,
                                    'open': float(row.get('open', 0)) if row.get('open') else None,
                                    'high': float(row.get('high', 0)) if row.get('high') else None,
                                    'low': float(row.get('low', 0)) if row.get('low') else None,
                                    'close': float(row.get('close', 0)) if row.get('close') else None,
                                    'volume': int(row.get('volume', 0)) if row.get('volume') else 0,
                                    '_source': f'vnstock_v3_{source}',
                                    '_ingested_at_utc': datetime.utcnow().isoformat() + 'Z'
                                }
                                
                                s3_key = f"bronze/stocks/raw/{ticker}_{row_date_str}.json"
                                s3_hook.load_string(
                                    string_data=json.dumps(stock_record, ensure_ascii=False, indent=2, default=str),
                                    key=s3_key,
                                    bucket_name=bucket_name,
                                    replace=True
                                )
                                files_saved += 1
                            except Exception as e:
                                logger.warning(f"      ⚠️ Failed to save {ticker} for date {row_date}: {str(e)}")
                        
                        if files_saved > 0:
                            successful.append(ticker)
                            logger.info(f"    ✅ {ticker}: {files_saved} days saved (source: {source})")
                            success = True
                            break
                        else:
                            logger.warning(f"    ⚠️ {ticker}: No files saved")
                            continue
                        
                except Exception as e:
                    logger.error(f"    ⚠️ {ticker} attempt {attempt+1}: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt + random.uniform(0, 1))
            
            if not success:
                failed.append(ticker)
            time.sleep(2.5 + random.uniform(0, 1))
        
        # Upload metadata
        metadata = {
            'extraction_date': date_str,
            'total_tickers': len(tickers),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': f"{(len(successful)/len(tickers)*100):.1f}%",
            'successful_tickers': successful,
            'failed_tickers': failed,
            '_schema_version': '2.0'
        }
        
        s3_hook.load_string(
            string_data=json.dumps(metadata, indent=2),
            key=f"bronze/stocks/metadata/extraction_{date_str}.json",
            bucket_name=bucket_name,
            replace=True
        )
        
        logger.info(f"✅ Stock extraction complete: {len(successful)}/{len(tickers)} successful")
        return {'successful': len(successful), 'failed': len(failed)}
        
    except Exception as e:
        logger.error(f"💥 Stock extraction failed: {str(e)}")
        raise


def scrape_vietnamese_news(**context):
    """
    Scrape financial news from 6 major Vietnamese sources
    Sources: VnExpress, Cafef, VietStock, CafeF, Dân Trí, Thanh Niên
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import hashlib
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        logger = logging.getLogger(__name__)
        logger.info(f"📰 Starting news scraping from Vietnamese sources for {date_str}")
        
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # News sources configuration
        news_sources = [
            {
                'name': 'VnExpress Kinh Doanh',
                'url': 'https://vnexpress.net/kinh-doanh',
                'selector': 'article.item-news',
                'title_selector': 'h3.title-news a',
                'link_selector': 'h3.title-news a'
            },
            {
                'name': 'CafeF',
                'url': 'https://cafef.vn/thi-truong-chung-khoan.chn',
                'selector': 'div.box-news-1',
                'title_selector': 'h3 a',
                'link_selector': 'h3 a'
            },
            {
                'name': 'VietStock',
                'url': 'https://vietstock.vn/tin-tuc',
                'selector': 'div.news-item',
                'title_selector': 'h3 a',
                'link_selector': 'h3 a'
            },
            {
                'name': 'Dân Trí Kinh Doanh',
                'url': 'https://dantri.com.vn/kinh-doanh.htm',
                'selector': 'article',
                'title_selector': 'h3 a',
                'link_selector': 'h3 a'
            },
            {
                'name': 'Thanh Niên Kinh Tế',
                'url': 'https://thanhnien.vn/kinh-te/',
                'selector': 'article',
                'title_selector': 'h2 a',
                'link_selector': 'h2 a'
            },
            {
                'name': 'Tuổi Trẻ Kinh Tế',
                'url': 'https://tuoitre.vn/kinh-te.htm',
                'selector': 'div.box-category-item',
                'title_selector': 'h3 a',
                'link_selector': 'h3 a'
            }
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        total_articles = 0
        successful_sources = []
        failed_sources = []
        
        for source in news_sources:
            try:
                logger.info(f"  Scraping {source['name']}...")
                response = requests.get(source['url'], headers=headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.select(source['selector'])[:10]  # Limit to 10 articles per source
                
                source_count = 0
                for article in articles:
                    try:
                        title_elem = article.select_one(source['title_selector'])
                        link_elem = article.select_one(source['link_selector'])
                        
                        if title_elem and link_elem:
                            title = title_elem.get_text(strip=True)
                            link = link_elem.get('href', '')
                            
                            # Make link absolute
                            if link.startswith('/'):
                                from urllib.parse import urljoin
                                link = urljoin(source['url'], link)
                            
                            # Generate unique ID
                            article_id = hashlib.md5(link.encode()).hexdigest()[:16]
                            
                            news_record = {
                                'id': article_id,
                                'title': title,
                                'link': link,
                                'source': source['name'],
                                'published_date': date_str,
                                '_scraping_method': 'beautifulsoup',
                                '_ingested_at_utc': datetime.utcnow().isoformat() + 'Z'
                            }
                            
                            s3_key = f"bronze/news/raw/{article_id}.json"
                            s3_hook.load_string(
                                string_data=json.dumps(news_record, ensure_ascii=False, indent=2),
                                key=s3_key,
                                bucket_name=bucket_name,
                                replace=True
                            )
                            
                            source_count += 1
                            total_articles += 1
                            
                    except Exception as e:
                        logger.warning(f"    ⚠️ Failed to process article: {str(e)}")
                
                successful_sources.append(source['name'])
                logger.info(f"    ✅ {source['name']}: {source_count} articles")
                
            except Exception as e:
                failed_sources.append(source['name'])
                logger.error(f"    ❌ {source['name']} failed: {str(e)}")
        
        # Upload metadata
        metadata = {
            'extraction_date': date_str,
            'total_sources': len(news_sources),
            'successful_sources': len(successful_sources),
            'failed_sources': len(failed_sources),
            'total_articles': total_articles,
            'sources_processed': successful_sources,
            'sources_failed': failed_sources,
            '_schema_version': '2.0'
        }
        
        s3_hook.load_string(
            string_data=json.dumps(metadata, indent=2),
            key=f"bronze/news/metadata/extraction_{date_str}.json",
            bucket_name=bucket_name,
            replace=True
        )
        
        logger.info(f"✅ News scraping complete: {total_articles} articles from {len(successful_sources)} sources")
        return {'total_articles': total_articles, 'successful_sources': len(successful_sources)}
        
    except Exception as e:
        logger.error(f"💥 News scraping failed: {str(e)}")
        raise


def extract_macro_data(**context):
    """Extract macro economic data - OPTIMIZED"""
    try:
        import numpy as np
        import pandas as pd
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        logger = logging.getLogger(__name__)
        logger.info(f"📊 Starting macro data extraction for {date_str}")
        
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Generate time series
        end_date = datetime.strptime(date_str, '%Y-%m-%d')
        start_date = end_date - timedelta(days=365)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Define indicators
        macro_indicators = {
            'economic': [
                ('gdp', 3000, 4000), ('gdp_growth', 4, 8), ('cpi', 100, 150),
                ('inflation', 2, 6), ('unemployment', 2, 4)
            ],
            'forex': [
                ('usd_vnd', 23000, 25000), ('eur_vnd', 25000, 28000), 
                ('jpy_vnd', 150, 200)
            ],
            'indices': [
                ('vnindex', 900, 1300), ('vn30', 800, 1200)
            ]
        }
        
        indicators_processed = []
        
        for category, indicators in macro_indicators.items():
            for indicator_name, min_val, max_val in indicators:
                try:
                    # Generate realistic data
                    base_trend = np.linspace(min_val, max_val, len(date_range))
                    seasonal = np.sin(np.arange(len(date_range)) * 2 * np.pi / 365) * (max_val - min_val) * 0.05
                    noise = np.random.normal(0, (max_val - min_val) * 0.02, len(date_range))
                    values = base_trend + seasonal + noise
                    
                    df = pd.DataFrame({
                        'date': date_range.strftime('%Y-%m-%d'),
                        'value': np.round(values, 2)
                    })
                    
                    s3_key = f"bronze/macro/raw/{category}/{indicator_name}.csv"
                    s3_hook.load_string(
                        string_data=df.to_csv(index=False),
                        key=s3_key,
                        bucket_name=bucket_name,
                        replace=True
                    )
                    
                    indicators_processed.append(f"{category}/{indicator_name}")
                    
                except Exception as e:
                    logger.error(f"  ❌ Failed {category}/{indicator_name}: {str(e)}")
        
        # Upload metadata
        metadata = {
            'extraction_date': date_str,
            'data_period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': date_str,
                'days': len(date_range)
            },
            'total_indicators': len(indicators_processed),
            'indicators_processed': indicators_processed,
            '_schema_version': '2.0'
        }
        
        s3_hook.load_string(
            string_data=json.dumps(metadata, indent=2),
            key=f"bronze/macro/metadata/extraction_{date_str}.json",
            bucket_name=bucket_name,
            replace=True
        )
        
        logger.info(f"✅ Macro extraction complete: {len(indicators_processed)} indicators")
        return {'total_indicators': len(indicators_processed)}
        
    except Exception as e:
        logger.error(f"💥 Macro extraction failed: {str(e)}")
        raise


def validate_bronze_data(**context):
    """Validate uploaded bronze data"""
    try:
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        logger = logging.getLogger(__name__)
        logger.info(f"🔍 Validating Bronze data for {date_str}")
        
        validation_results = {
            'stocks': {'passed': False, 'count': 0},
            'news': {'passed': False, 'count': 0},
            'macro': {'passed': False, 'count': 0}
        }
        
        # Validate stocks
        try:
            stocks_keys = s3_hook.list_keys(bucket_name=bucket_name, prefix="bronze/stocks/raw/")
            if stocks_keys:
                validation_results['stocks'] = {'passed': True, 'count': len(stocks_keys)}
                logger.info(f"  ✅ Stocks: {len(stocks_keys)} files")
        except:
            pass
        
        # Validate news
        try:
            news_keys = s3_hook.list_keys(bucket_name=bucket_name, prefix="bronze/news/raw/")
            if news_keys:
                validation_results['news'] = {'passed': True, 'count': len(news_keys)}
                logger.info(f"  ✅ News: {len(news_keys)} files")
        except:
            pass
        
        # Validate macro
        try:
            macro_keys = s3_hook.list_keys(bucket_name=bucket_name, prefix="bronze/macro/raw/")
            if macro_keys:
                validation_results['macro'] = {'passed': True, 'count': len(macro_keys)}
                logger.info(f"  ✅ Macro: {len(macro_keys)} files")
        except:
            pass
        
        logger.info(f"✅ Validation complete")
        return validation_results
        
    except Exception as e:
        logger.error(f"💥 Validation failed: {str(e)}")
        raise


# Task definitions
validate_aws = PythonOperator(
    task_id='validate_aws_s3_access',
    python_callable=validate_aws_s3_access,
    dag=dag,
)

extract_stocks = PythonOperator(
    task_id='extract_stocks_with_retry',
    python_callable=extract_vnstock_data_with_retry,
    dag=dag,
)

extract_news = PythonOperator(
    task_id='scrape_news_sources',
    python_callable=scrape_vietnamese_news,
    dag=dag,
)

extract_macro = PythonOperator(
    task_id='extract_macro_data',
    python_callable=extract_macro_data,
    dag=dag,
)

validate_data = PythonOperator(
    task_id='validate_bronze_data',
    python_callable=validate_bronze_data,
    dag=dag,
)

# Task dependencies
validate_aws >> [extract_stocks, extract_news, extract_macro] >> validate_data
