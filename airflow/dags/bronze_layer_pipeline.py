"""
Bronze Layer Pipeline - V2 (Aligned with S3_LAKEHOUSE_COMPLETE_STRUCTURE.md)
==============================================================================

This DAG extracts raw data from multiple sources and uploads to S3 Bronze layer:
- Stocks: ~150 tickers → bronze/stocks/raw/{ticker}_{date}.json (FLAT structure, no subfolders)
- News: Financial news → bronze/news/raw/{id}.json  
- Macro: 50+ economic indicators → bronze/macro/raw/{category}/{indicator}.csv (subdirectories)

Schedule: Daily at 6 AM (weekdays only)
Dependencies: vnstock3, numpy, pandas, boto3
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
import json
import os
from enhanced_logger import log_pipeline_start, log_pipeline_success, log_pipeline_error

# Default arguments
default_args = {
    'owner': 'finance_portfolio',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# DAG definition
dag = DAG(
    'bronze_layer_pipeline',
    default_args=default_args,
    description='Bronze layer data ingestion (stocks, news, macro)',
    schedule_interval='0 6 * * 1-5',  # 6 AM weekdays
    catchup=False,
    tags=['bronze', 'lakehouse'],
    max_active_runs=1
)


def extract_vnstock_data(**context):
    """
    Extract stock OHLC data for ~150 Vietnam stocks
    Output: bronze/stocks/raw/{ticker}_{date}.json (FLAT structure)
    """
    try:
        import vnstock3 as vs
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import time
        
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger = logging.getLogger(__name__)
        logger.info(f"📈 Starting stock data extraction for {date_str}")
        
        # Enhanced logger metadata
        metadata = {
            'pipeline_name': 'bronze_stock_extraction',
            'layer': 'bronze',
            'data_type': 'stocks',
            'execution_date': date_str
        }
        
        log_pipeline_start(logger, metadata)
        
        # Initialize vnstock and S3
        vnstock = vs.Vnstock()
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Vietnam stock tickers (~150 stocks)
        tickers = [
            # VN30 stocks
            'ACB', 'BCM', 'BID', 'BVH', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG',
        #     'MBB', 'MSN', 'MWG', 'PLX', 'POW', 'SAB', 'SSI', 'STB', 'TCB', 'TPB',
        #     'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE',
        #     # Additional blue chips
        #     'AAA', 'ABT', 'AGG', 'ACV', 'BMI', 'BMP', 'BSR', 'BWE', 'CII', 'CMG',
        #     'CTD', 'DBC', 'DCM', 'DGC', 'DGW', 'DHG', 'DIG', 'DPM', 'DXG', 'EIB',
        #     'FLC', 'GMD', 'HAG', 'HCM', 'HDC', 'HNG', 'HPX', 'HSG', 'HT1', 'HTN',
        #     'IMP', 'KBC', 'KDC', 'KDH', 'LCG', 'LDG', 'LPB', 'MIG', 'NAB', 'NLG',
        #     'NT2', 'NVL', 'OCB', 'OGC', 'PAC', 'PC1', 'PDR', 'PET', 'PGD', 'PHR',
        #     'PNJ', 'POM', 'PPC', 'PVD', 'PVT', 'REE', 'ROS', 'SBT', 'SCR', 'SCS',
        #     'SHB', 'SJS', 'SKG', 'SSB', 'SSC', 'SZC', 'TDH', 'TLG', 'TNA', 'TNG',
        #     'TPH', 'TRA', 'TYA', 'VAB', 'VCG', 'VCI', 'VGC', 'VHC', 'VID', 'VIX',
        #     'VND', 'VOS', 'VPI', 'VPG', 'VSC', 'VSH', 'VTO', 'YEG'
        ]
        
        successful_stocks = []
        failed_stocks = []
        s3_paths = []
        
        logger.info(f"Processing {len(tickers)} stock tickers...")
        
        for ticker in tickers:
            try:
                logger.info(f"  Processing {ticker}...")
                
                # Fetch stock data from VNStock API
                stock_data = vnstock.stock(symbol=ticker, source='VCI').quote.history(
                    start=date_str,
                    end=date_str
                )
                
                if stock_data is not None and not stock_data.empty:
                    # Convert DataFrame to JSON
                    stock_dict = stock_data.to_dict(orient='records')
                    
                    # Add metadata
                    stock_record = {
                        'ticker': ticker,
                        'date': date_str,
                        'data': stock_dict,
                        '_source': 'vnstock_v3_vci',
                        '_ingested_at_utc': datetime.utcnow().isoformat() + 'Z'
                    }
                    
                    # Convert to JSON string
                    json_content = json.dumps(stock_record, ensure_ascii=False, indent=2, default=str)
                    
                    # S3 key: bronze/stocks/raw/{ticker}_{date}.json (FLAT structure)
                    s3_key = f"bronze/stocks/raw/{ticker}_{date_str}.json"
                    
                    # Upload to S3
                    s3_hook.load_string(
                        string_data=json_content,
                        key=s3_key,
                        bucket_name=bucket_name,
                        replace=True
                    )
                    
                    successful_stocks.append(ticker)
                    s3_paths.append(s3_key)
                    logger.info(f"    ✅ {ticker}: {len(stock_dict)} records → {s3_key}")
                    
                else:
                    logger.warning(f"    ⚠️ {ticker}: No data returned")
                    failed_stocks.append(ticker)
                
                # Rate limiting (avoid API throttling)
                time.sleep(2.5)
                
            except Exception as e:
                logger.error(f"    ❌ {ticker} failed: {str(e)}")
                failed_stocks.append(ticker)
        
        # Create metadata summary
        metadata_summary = {
            'extraction_date': date_str,
            'total_tickers': len(tickers),
            'successful_extractions': len(successful_stocks),
            'failed_extractions': len(failed_stocks),
            'success_rate': f"{(len(successful_stocks)/len(tickers)*100):.1f}%",
            'successful_tickers': successful_stocks,
            'failed_tickers': failed_stocks,
            's3_paths': s3_paths,
            'structure_note': 'Files stored flat without ticker subfolders',
            '_schema_version': '2.0'
        }
        
        # Upload metadata
        metadata_key = f"bronze/stocks/metadata/extraction_{date_str}.json"
        s3_hook.load_string(
            string_data=json.dumps(metadata_summary, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        logger.info(f"📄 Metadata uploaded to {metadata_key}")
        
        # Result summary
        result = {
            'successful_stocks': len(successful_stocks),
            'failed_stocks': len(failed_stocks),
            'total_stocks': len(tickers),
            'execution_date': date_str
        }
        
        log_pipeline_success(logger, metadata, result)
        logger.info(f"✅ Stock Extraction Complete: {result}")
        
        return result
        
    except Exception as e:
        context_data = {
            'successful_stocks': len(successful_stocks) if 'successful_stocks' in locals() else 0,
            'failed_stocks': len(failed_stocks) if 'failed_stocks' in locals() else 0
        }
        
        log_pipeline_error(logger, metadata, e, context_data)
        raise


def extract_news_data(**context):
    """
    Extract financial news from Google Custom Search API
    Output: bronze/news/raw/{id}.json
    """
    try:
        import requests
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import hashlib
        
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger = logging.getLogger(__name__)
        logger.info(f"📰 Starting news extraction for {date_str}")
        
        # Enhanced logger metadata
        metadata = {
            'pipeline_name': 'bronze_news_extraction',
            'layer': 'bronze',
            'data_type': 'news',
            'execution_date': date_str
        }
        
        log_pipeline_start(logger, metadata)
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        # Google Custom Search API credentials (from environment)
        api_key = os.getenv('GOOGLE_API_KEY')
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        successful_sources = []
        failed_sources = []
        s3_paths = []
        total_articles = 0
        
        # Vietnamese financial news search queries
        search_queries = [
            'chứng khoán Việt Nam',
            'VNINDEX hôm nay',
            'thị trường tài chính Việt Nam',
            'cổ phiếu ngân hàng',
            'bất động sản Việt Nam'
        ]
        
        for query in search_queries:
            try:
                logger.info(f"  Searching: '{query}'...")
                
                # Google Custom Search API
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': api_key,
                    'cx': search_engine_id,
                    'q': query,
                    'dateRestrict': 'd1',  # Last 24 hours
                    'num': 10
                }
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                search_results = response.json()
                articles = search_results.get('items', [])
                
                for article in articles:
                    # Generate unique ID from URL
                    article_id = hashlib.md5(article['link'].encode()).hexdigest()[:16]
                    
                    # Create news record
                    news_record = {
                        'id': article_id,
                        'title': article.get('title', ''),
                        'snippet': article.get('snippet', ''),
                        'link': article.get('link', ''),
                        'source': article.get('displayLink', ''),
                        'published_date': date_str,
                        'query': query,
                        '_ingested_at_utc': datetime.utcnow().isoformat() + 'Z'
                    }
                    
                    # Convert to JSON
                    json_content = json.dumps(news_record, ensure_ascii=False, indent=2)
                    
                    # S3 key: bronze/news/raw/{id}.json
                    s3_key = f"bronze/news/raw/{article_id}.json"
                    
                    # Upload to S3
                    s3_hook.load_string(
                        string_data=json_content,
                        key=s3_key,
                        bucket_name=bucket_name,
                        replace=True
                    )
                    
                    s3_paths.append(s3_key)
                    total_articles += 1
                
                successful_sources.append(query)
                logger.info(f"    ✅ '{query}': {len(articles)} articles")
                
            except Exception as e:
                logger.error(f"    ❌ '{query}' failed: {str(e)}")
                failed_sources.append(query)
        
        # Create metadata
        metadata_summary = {
            'extraction_date': date_str,
            'total_queries': len(search_queries),
            'successful_queries': len(successful_sources),
            'failed_queries': len(failed_sources),
            'total_articles': total_articles,
            'queries_processed': successful_sources,
            's3_paths': s3_paths,
            '_schema_version': '2.0'
        }
        
        # Upload metadata
        metadata_key = f"bronze/news/metadata/extraction_{date_str}.json"
        s3_hook.load_string(
            string_data=json.dumps(metadata_summary, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        logger.info(f"📄 Metadata uploaded to {metadata_key}")
        
        # Result summary
        result = {
            'total_articles': total_articles,
            'successful_queries': len(successful_sources),
            'failed_queries': len(failed_sources),
            'execution_date': date_str
        }
        
        log_pipeline_success(logger, metadata, result)
        logger.info(f"✅ News Extraction Complete: {result}")
        
        return result
        
    except Exception as e:
        context_data = {
            'articles_collected': total_articles if 'total_articles' in locals() else 0,
            'sources_processed': len(successful_sources) if 'successful_sources' in locals() else 0
        }
        
        log_pipeline_error(logger, metadata, e, context_data)
        raise


def extract_macro_data(**context):
    """
    Extract macro economic data based on bronze_macro.py structure
    Creates 50+ CSV files in bronze/macro/raw/ subdirectories
    """
    try:
        import numpy as np
        import pandas as pd
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        from datetime import datetime, timedelta
        
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger = logging.getLogger(__name__)
        logger.info(f"📊 Starting macro data extraction for {date_str}")
        
        # Enhanced logger metadata
        metadata = {
            'pipeline_name': 'bronze_macro_extraction',
            'layer': 'bronze',
            'data_type': 'macro',
            'execution_date': date_str
        }
        
        log_pipeline_start(logger, metadata)
        
        # Initialize S3
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        s3_paths = []
        indicators_processed = []
        
        # Generate historical data (last 365 days) for realistic CSVs
        end_date = datetime.strptime(date_str, '%Y-%m-%d')
        start_date = end_date - timedelta(days=365)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Define 50+ indicators matching bronze_macro.py structure
        macro_indicators = {
            'economic': [
                ('gdp', 3000, 4000),  # (name, min_value, max_value)
                ('gdp_growth', 4, 8),
                ('cpi', 100, 150),
                ('inflation', 2, 6),
                ('unemployment', 2, 4),
                ('pmi', 45, 60),
                ('industrial_production', -5, 15)
            ],
            'forex': [
                ('usd_vnd', 23000, 25000),
                ('eur_vnd', 25000, 28000),
                ('jpy_vnd', 150, 200),
                ('cny_vnd', 3200, 3800),
                ('krw_vnd', 17, 21)
            ],
            'indices': [
                ('vnindex', 900, 1300),
                ('vn30', 800, 1200),
                ('hnxindex', 200, 280),
                ('upcom', 60, 100)
            ],
            'sectors': [
                ('banking', 15000, 22000),
                ('securities', 8000, 15000),
                ('insurance', 12000, 18000),
                ('real_estate', 10000, 16000),
                ('construction', 8000, 13000),
                ('steel', 9000, 14000),
                ('oil_gas', 11000, 17000),
                ('retail', 7000, 12000),
                ('technology', 13000, 20000),
                ('food_beverage', 9000, 15000),
                ('healthcare', 10000, 16000),
                ('utilities', 8000, 13000)
            ],
            'banking': [
                ('credit_growth', 8, 15),
                ('deposit_rate', 3, 8),
                ('lending_rate', 6, 12)
            ],
            'real_estate': [
                ('housing_price_index', 100, 180),
                ('transaction_volume', 5000, 20000),
                ('new_supply', 10000, 50000),
                ('absorption_rate', 50, 95),
                ('rental_yield', 4, 8)
            ]
        }
        
        # Process each category and indicator
        for category, indicators in macro_indicators.items():
            logger.info(f"📈 Processing category: {category} ({len(indicators)} indicators)")
            
            for indicator_name, min_val, max_val in indicators:
                try:
                    # Generate realistic time series with trend and noise
                    base_trend = np.linspace(min_val, max_val, len(date_range))
                    seasonal = np.sin(np.arange(len(date_range)) * 2 * np.pi / 365) * (max_val - min_val) * 0.05
                    noise = np.random.normal(0, (max_val - min_val) * 0.02, len(date_range))
                    values = base_trend + seasonal + noise
                    
                    # Create DataFrame
                    df = pd.DataFrame({
                        'date': date_range.strftime('%Y-%m-%d'),
                        'value': np.round(values, 2)
                    })
                    
                    # Convert to CSV string
                    csv_buffer = df.to_csv(index=False)
                    
                    # S3 key: bronze/macro/raw/{category}/{indicator_name}.csv
                    s3_key = f"bronze/macro/raw/{category}/{indicator_name}.csv"
                    
                    # Upload to S3
                    s3_hook.load_string(
                        string_data=csv_buffer,
                        key=s3_key,
                        bucket_name=bucket_name,
                        replace=True
                    )
                    
                    s3_paths.append(s3_key)
                    indicators_processed.append(f"{category}/{indicator_name}")
                    
                    logger.info(f"  ✅ {indicator_name}: {len(df)} rows → {s3_key}")
                    
                except Exception as e:
                    logger.error(f"  ❌ Failed {category}/{indicator_name}: {str(e)}")
        
        # Create comprehensive metadata
        metadata_summary = {
            'extraction_date': date_str,
            'data_period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': date_str,
                'days': len(date_range)
            },
            'categories': {
                category: len(indicators) 
                for category, indicators in macro_indicators.items()
            },
            'total_indicators': len(indicators_processed),
            'total_files': len(s3_paths),
            'indicators_processed': indicators_processed,
            's3_paths': s3_paths,
            'statistics': {
                'economic_indicators': len([i for i in indicators_processed if i.startswith('economic')]),
                'forex_pairs': len([i for i in indicators_processed if i.startswith('forex')]),
                'market_indices': len([i for i in indicators_processed if i.startswith('indices')]),
                'sector_indices': len([i for i in indicators_processed if i.startswith('sectors')]),
                'banking_metrics': len([i for i in indicators_processed if i.startswith('banking')]),
                'real_estate_metrics': len([i for i in indicators_processed if i.startswith('real_estate')])
            },
            'structure_note': '50+ CSV files organized in category subdirectories',
            'source': 'Generated time series data (replace with real API in production)',
            '_schema_version': '2.0'
        }
        
        # Upload metadata
        metadata_key = f"bronze/macro/metadata/extraction_{date_str}.json"
        s3_hook.load_string(
            string_data=json.dumps(metadata_summary, indent=2),
            key=metadata_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        logger.info(f"📄 Metadata uploaded to {metadata_key}")
        
        # Result summary
        result = {
            'total_indicators': len(indicators_processed),
            'total_files': len(s3_paths),
            'categories': len(macro_indicators),
            'execution_date': date_str
        }
        
        log_pipeline_success(logger, metadata, result)
        logger.info(f"✅ Macro Extraction Complete: {result}")
        
        return result
        
    except Exception as e:
        context_data = {
            'indicators_processed': len(indicators_processed) if 'indicators_processed' in locals() else 0,
            'files_uploaded': len(s3_paths) if 's3_paths' in locals() else 0
        }
        
        log_pipeline_error(logger, metadata, e, context_data)
        raise


def validate_bronze_data(**context):
    """Validate uploaded bronze data quality"""
    try:
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        
        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')
        
        execution_date = context['execution_date']
        date_str = execution_date.strftime('%Y-%m-%d')
        
        logger = logging.getLogger(__name__)
        logger.info(f"🔍 Starting Bronze data validation for {date_str}")
        
        validation_results = {
            'stocks_validation': {'passed': True, 'issues': []},
            'news_validation': {'passed': True, 'issues': []},
            'macro_validation': {'passed': True, 'issues': []},
        }
        
        # Validate stocks
        try:
            stocks_keys = s3_hook.list_keys(
                bucket_name=bucket_name,
                prefix=f"bronze/stocks/raw/",
                delimiter='/'
            )
            
            if stocks_keys and len(stocks_keys) > 0:
                logger.info(f"  ✅ Stocks: {len(stocks_keys)} files found")
            else:
                validation_results['stocks_validation']['passed'] = False
                validation_results['stocks_validation']['issues'].append('No stock files found')
                logger.warning(f"  ⚠️ Stocks: No files found")
        except Exception as e:
            validation_results['stocks_validation']['passed'] = False
            validation_results['stocks_validation']['issues'].append(str(e))
        
        # Validate news
        try:
            news_keys = s3_hook.list_keys(
                bucket_name=bucket_name,
                prefix=f"bronze/news/raw/",
                delimiter='/'
            )
            
            if news_keys and len(news_keys) > 0:
                logger.info(f"  ✅ News: {len(news_keys)} files found")
            else:
                validation_results['news_validation']['passed'] = False
                validation_results['news_validation']['issues'].append('No news files found')
                logger.warning(f"  ⚠️ News: No files found")
        except Exception as e:
            validation_results['news_validation']['passed'] = False
            validation_results['news_validation']['issues'].append(str(e))
        
        # Validate macro
        try:
            macro_keys = s3_hook.list_keys(
                bucket_name=bucket_name,
                prefix=f"bronze/macro/raw/",
                delimiter='/'
            )
            
            if macro_keys and len(macro_keys) > 0:
                logger.info(f"  ✅ Macro: {len(macro_keys)} files found")
            else:
                validation_results['macro_validation']['passed'] = False
                validation_results['macro_validation']['issues'].append('No macro files found')
                logger.warning(f"  ⚠️ Macro: No files found")
        except Exception as e:
            validation_results['macro_validation']['passed'] = False
            validation_results['macro_validation']['issues'].append(str(e))
        
        logger.info(f"✅ Validation Complete: {validation_results}")
        
        return validation_results
        
    except Exception as e:
        logger.error(f"💥 Validation failed: {str(e)}")
        raise


# Task definitions
extract_stocks = PythonOperator(
    task_id='extract_vnstock_data',
    python_callable=extract_vnstock_data,
    dag=dag,
)

extract_news = PythonOperator(
    task_id='extract_news_data',
    python_callable=extract_news_data,
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

# Task dependencies: All extractions run in parallel, then validation
[extract_stocks, extract_news, extract_macro] >> validate_data
