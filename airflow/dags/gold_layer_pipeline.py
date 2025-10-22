# Gold Layer Pipeline - 4-Layer Analytics Architecture"""""""""""""""

# Creates analytics-ready datasets with technical indicators, sentiment analysis,

# serving cache, and pipeline metadata trackingGold Layer Pipeline - 4-Layer Analytics Architecture



from datetime import datetime, timedelta=====================================================Gold Layer Pipeline - 4-Layer Analytics Architecture

from airflow import DAG

from airflow.operators.python import PythonOperator

from airflow.providers.amazon.aws.hooks.s3 import S3Hook

import pandas as pdCreates analytics-ready datasets with technical indicators, sentiment analysis,=====================================================Gold Layer Pipeline (Aligned with S3_LAKEHOUSE_COMPLETE_STRUCTURE.md)

import numpy as np

from io import BytesIOserving cache, and pipeline metadata tracking.

import json

import logging

import sys

4-Layer Architecture:

sys.path.append('/opt/airflow/dags')

from enhanced_logger import log_pipeline_start, log_pipeline_success, log_pipeline_error1. analytics/ - Market features (MA, RSI, volatility)Layer 1: Analytics - market_features with technical indicators========================================================================Gold Layer Pipeline (Aligned with S3_LAKEHOUSE_COMPLETE_STRUCTURE.md)Gold Layer DAG - Analytics & ML Feature Engineering with Spark



S3_BUCKET = 'bankanalystportfolio'2. sentiment_analysis/ - News sentiment by date/source

S3_CONN_ID = 'aws_s3_conn'

3. serving/ - Pre-aggregated BI cacheLayer 2: Sentiment Analysis - news sentiment aggregation  

default_args = {

    'owner': 'finance_portfolio',4. metadata/ - Pipeline lineage tracking

    'depends_on_past': False,

    'start_date': datetime(2024, 1, 1),Layer 3: Serving - pre-aggregated BI cache

    'email_on_failure': False,

    'email_on_retry': False,Author: finance_portfolio

    'retries': 2,

    'retry_delay': timedelta(minutes=5),"""Layer 4: Metadata - pipeline lineage tracking

}



dag = DAG(

    'gold_layer_pipeline',from datetime import datetime, timedeltaThis DAG creates analytics tables from Silver layer with 4-layer architecture:========================================================================Creates business intelligence views and ML-ready datasets

    default_args=default_args,

    description='Gold Layer - 4-Layer Analytics Architecture',from airflow import DAG

    schedule_interval='0 8 * * 1-5',

    catchup=False,from airflow.operators.python import PythonOperatorSchedule: 8 AM weekdays after Silver layer

    tags=['gold', 'analytics', 'ml-features']

)from airflow.providers.amazon.aws.hooks.s3 import S3Hook



import pandas as pd"""

def calculate_technical_indicators(df):

    df = df.sort_values('date')import numpy as np

    df['MA_5'] = df['close'].rolling(window=5).mean()

    df['MA_10'] = df['close'].rolling(window=10).mean()from io import BytesIO

    df['MA_20'] = df['close'].rolling(window=20).mean()

    df['MA_30'] = df['close'].rolling(window=30).mean()import json

    

    delta = df['close'].diff()import loggingfrom airflow import DAGLayer 1 - ANALYTICS: Business intelligence tables

    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()

    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

    rs = gain / loss

    df['RSI_14'] = 100 - (100 / (1 + rs))# Import enhanced loggerfrom airflow.operators.python import PythonOperator

    df['volatility_7d'] = df['close'].rolling(window=7).std()

    return dfimport sys



sys.path.append('/opt/airflow/dags')from datetime import datetime, timedelta  - market_features: Technical indicators (MA, RSI, volatility)

def create_market_features(**context):

    execution_date = context['execution_date']from enhanced_logger import log_pipeline_start, log_pipeline_success, log_pipeline_error

    log_pipeline_start('gold_layer', 'create_market_features', execution_date)

    import logging

    try:

        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)# Configuration

        end_date = execution_date.date()

        start_date = end_date - timedelta(days=30)S3_BUCKET = 'bankanalystportfolio'import json  - sector_performance: Sector aggregationsThis DAG creates analytics tables from Silver layer with 4-layer architecture:Author: Banking Portfolio Team

        logging.info(f"Processing stocks from {start_date} to {end_date}")

        S3_CONN_ID = 'aws_s3_conn'

        silver_prefix = 'silver/stocks/'

        all_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=silver_prefix)import os

        

        if not all_files:default_args = {

            logging.warning("No Silver stock files found")

            return    'owner': 'finance_portfolio',import pandas as pd  - news_summary: Daily news aggregation

        

        stock_files = [f for f in all_files if f.endswith('.parquet') and 'partition_date=' in f]    'depends_on_past': False,

        all_stocks = []

            'start_date': datetime(2024, 1, 1),import numpy as np

        for file_key in stock_files:

            try:    'email_on_failure': False,

                partition_str = file_key.split('partition_date=')[1].split('/')[0]

                partition_date = datetime.strptime(partition_str, '%Y-%m-%d').date()    'email_on_retry': False,import io  - macro_indicators: Macro trends with moving averagesVersion: 2.0 (Spark-enabled)

                

                if start_date <= partition_date <= end_date:    'retries': 2,

                    obj = s3_hook.get_key(file_key, bucket_name=S3_BUCKET)

                    parquet_data = obj.get()['Body'].read()    'retry_delay': timedelta(minutes=5),

                    df = pd.read_parquet(BytesIO(parquet_data))

                    all_stocks.append(df)}

            except Exception as e:

                logging.error(f"Error reading {file_key}: {e}")from enhanced_logger import log_pipeline_start, log_pipeline_success, log_pipeline_error

                continue

        dag = DAG(

        if not all_stocks:

            logging.warning("No stock data in date range")    'gold_layer_pipeline',

            return

            default_args=default_args,

        stocks_df = pd.concat(all_stocks, ignore_index=True)

        results = []    description='Gold Layer - 4-Layer Analytics Architecture',# Default argumentsLayer 2 - SENTIMENT_ANALYSIS: Sentiment aggregationsLayer 1 - ANALYTICS: Business intelligence tablesDate: October 2025

        for ticker in stocks_df['ticker'].unique():

            ticker_df = stocks_df[stocks_df['ticker'] == ticker].copy()    schedule_interval='0 8 * * 1-5',  # 8 AM weekdays

            ticker_df = calculate_technical_indicators(ticker_df)

            results.append(ticker_df)    catchup=False,default_args = {

        

        market_features_df = pd.concat(results, ignore_index=True)    tags=['gold', 'analytics', 'ml-features']

        partition_date_str = end_date.strftime('%Y-%m-%d')

        gold_prefix = f'gold/analytics/market_features/partition_date={partition_date_str}/')    'owner': 'finance_portfolio',  - News sentiment by date/source

        

        parquet_buffer = BytesIO()

        market_features_df.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)

        parquet_buffer.seek(0)    'depends_on_past': False,

        

        s3_key = f'{gold_prefix}market_features_{end_date.strftime("%Y%m%d")}.parquet'def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:

        s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)

            """Calculate technical indicators for stock data"""    'start_date': datetime(2024, 1, 1),  - market_features: Technical indicators (MA, RSI, volatility)"""

        metadata = {

            'execution_date': execution_date.isoformat(),    df = df.sort_values('date')

            'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()},

            'records_processed': len(market_features_df),        'email_on_failure': True,

            'tickers_count': market_features_df['ticker'].nunique(),

            'features': ['MA_5', 'MA_10', 'MA_20', 'MA_30', 'RSI_14', 'volatility_7d']    # Moving Averages

        }

            df['MA_5'] = df['close'].rolling(window=5).mean()    'email_on_retry': False,Layer 3 - SERVING: Pre-aggregated cache for BI dashboards

        metadata_key = f'{gold_prefix}_metadata.json'

        s3_hook.load_string(json.dumps(metadata, indent=2), key=metadata_key, bucket_name=S3_BUCKET, replace=True)    df['MA_10'] = df['close'].rolling(window=10).mean()

        

        log_pipeline_success('gold_layer', 'create_market_features', len(market_features_df))    df['MA_20'] = df['close'].rolling(window=20).mean()    'retries': 3,

        logging.info(f"Market features created: {len(market_features_df)} records")

            df['MA_30'] = df['close'].rolling(window=30).mean()

    except Exception as e:

        log_pipeline_error('gold_layer', 'create_market_features', str(e))        'retry_delay': timedelta(minutes=5),  - market_dashboard, sentiment_features, macro_features, risk_metrics  - sector_performance: Sector aggregations

        raise

    # RSI (14-day)



def create_sentiment_analysis(**context):    delta = df['close'].diff()    'execution_timeout': timedelta(hours=4),

    execution_date = context['execution_date']

    log_pipeline_start('gold_layer', 'create_sentiment_analysis', execution_date)    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()

    

    try:    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()}

        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)

        end_date = execution_date.date()    rs = gain / loss

        start_date = end_date - timedelta(days=7)

        logging.info(f"Processing news from {start_date} to {end_date}")    df['RSI_14'] = 100 - (100 / (1 + rs))

        

        silver_prefix = 'silver/news/'    

        all_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=silver_prefix)

            # Volatility (7-day)# DAG definitionLayer 4 - METADATA: Pipeline lineage and quality tracking  - news_summary: Daily news aggregationfrom datetime import datetime, timedelta

        if not all_files:

            logging.warning("No Silver news files found")    df['volatility_7d'] = df['close'].rolling(window=7).std()

            return

            dag = DAG(

        news_files = [f for f in all_files if f.endswith('.parquet') and 'partition_date=' in f]

        all_news = []    return df

        

        for file_key in news_files:    'gold_layer_pipeline',  - pipeline_runs: Execution tracking with lineage

            try:

                partition_str = file_key.split('partition_date=')[1].split('/')[0]

                partition_date = datetime.strptime(partition_str, '%Y-%m-%d').date()

                def create_market_features(**context):    default_args=default_args,

                if start_date <= partition_date <= end_date:

                    obj = s3_hook.get_key(file_key, bucket_name=S3_BUCKET)    """

                    parquet_data = obj.get()['Body'].read()

                    df = pd.read_parquet(BytesIO(parquet_data))    Layer 1 - ANALYTICS: Market Features    description='Gold layer - 4-layer analytics architecture',  - quality_metrics: Data quality per table  - macro_indicators: Macro trends with moving averagesfrom airflow import DAG

                    all_news.append(df)

            except Exception as e:    Read last 30 days of Silver stocks data, calculate technical indicators

                logging.error(f"Error reading {file_key}: {e}")

                continue    """    schedule_interval='0 8 * * 1-5',

        

        if not all_news:    execution_date = context['execution_date']

            logging.warning("No news data in date range")

            return    log_pipeline_start('gold_layer', 'create_market_features', execution_date)    catchup=False,

        

        news_df = pd.concat(all_news, ignore_index=True)    

        

        if 'published_date' in news_df.columns:    try:    tags=['gold', 'analytics'],

            news_df['date'] = pd.to_datetime(news_df['published_date']).dt.date

                s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)

        sentiment_agg = news_df.groupby(['date', 'source']).agg({

            'sentiment_score': ['mean', 'std', 'count'],            max_active_runs=1Schedule: Daily at 8 AM (weekdays), after Silver layerfrom airflow.operators.python import PythonOperator

            'title': 'count'

        }).reset_index()        # Date range for last 30 days

        

        sentiment_agg.columns = ['date', 'source', 'avg_sentiment', 'sentiment_std', 'sentiment_count', 'news_count']        end_date = execution_date.date())

        

        partition_date_str = end_date.strftime('%Y-%m-%d')        start_date = end_date - timedelta(days=30)

        gold_prefix = f'gold/sentiment_analysis/partition_date={partition_date_str}/'

                Dependencies: pandas, pyarrow, numpy

        parquet_buffer = BytesIO()

        sentiment_agg.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)        logging.info(f"Processing stocks from {start_date} to {end_date}")

        parquet_buffer.seek(0)

                

        s3_key = f'{gold_prefix}sentiment_agg_{end_date.strftime("%Y%m%d")}.parquet'

        s3_hook.load_bytes(parquet_buffer.read(), key=s3_key, bucket_name=S3_BUCKET, replace=True)        # List all stock files in Silver layer

        

        metadata = {        silver_prefix = 'silver/stocks/'def create_market_features(**context):"""Layer 2 - SENTIMENT_ANALYSIS: Sentiment aggregationsfrom airflow.operators.bash import BashOperator

            'execution_date': execution_date.isoformat(),

            'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()},        all_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=silver_prefix)

            'aggregations': len(sentiment_agg),

            'news_processed': len(news_df),            """Layer 1: Create market_features with technical indicators"""

            'sources': news_df['source'].unique().tolist() if 'source' in news_df.columns else []

        }        if not all_files:

        

        metadata_key = f'{gold_prefix}_metadata.json'            logging.warning("No Silver stock files found")    try:

        s3_hook.load_string(json.dumps(metadata, indent=2), key=metadata_key, bucket_name=S3_BUCKET, replace=True)

                    return

        log_pipeline_success('gold_layer', 'create_sentiment_analysis', len(sentiment_agg))

        logging.info(f"Sentiment analysis created: {len(sentiment_agg)} aggregations")                from airflow.providers.amazon.aws.hooks.s3 import S3Hook

        

    except Exception as e:        # Filter parquet files in date range

        log_pipeline_error('gold_layer', 'create_sentiment_analysis', str(e))

        raise        stock_files = [f for f in all_files if f.endswith('.parquet') and 'partition_date=' in f]        from airflow import DAG  - News sentiment by date/sourcefrom airflow.operators.dummy import DummyOperator



        

def create_serving_cache(**context):

    execution_date = context['execution_date']        all_stocks = []        execution_date = context['execution_date']

    log_pipeline_start('gold_layer', 'create_serving_cache', execution_date)

            

    try:

        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)        # Read stock files        date_str = execution_date.strftime('%Y-%m-%d')from airflow.operators.python import PythonOperator

        end_date = execution_date.date()

        partition_date_str = end_date.strftime('%Y-%m-%d')        for file_key in stock_files:

        

        market_prefix = f'gold/analytics/market_features/partition_date={partition_date_str}/'            try:        

        market_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=market_prefix)

        market_parquet = [f for f in market_files if f.endswith('.parquet')]                # Extract partition date

        

        if not market_parquet:                partition_str = file_key.split('partition_date=')[1].split('/')[0]        logger = logging.getLogger(__name__)from datetime import datetime, timedeltafrom airflow.providers.amazon.aws.hooks.s3 import S3Hook

            logging.warning("No market features found")

            return                partition_date = datetime.strptime(partition_str, '%Y-%m-%d').date()

        

        obj = s3_hook.get_key(market_parquet[0], bucket_name=S3_BUCKET)                        logger.info(f"📊 Creating market features for {date_str}")

        market_df = pd.read_parquet(BytesIO(obj.get()['Body'].read()))

                        if start_date <= partition_date <= end_date:

        latest_data = market_df.sort_values('date').groupby('ticker').last().reset_index()

        latest_data['price_change_pct'] = ((latest_data['close'] - latest_data['open']) / latest_data['open'] * 100)                    obj = s3_hook.get_key(file_key, bucket_name=S3_BUCKET)        import logging

        

        top_gainers = latest_data.nlargest(10, 'price_change_pct')[['ticker', 'close', 'price_change_pct', 'volume', 'RSI_14']]                    parquet_data = obj.get()['Body'].read()

        top_losers = latest_data.nsmallest(10, 'price_change_pct')[['ticker', 'close', 'price_change_pct', 'volume', 'RSI_14']]

                            df = pd.read_parquet(BytesIO(parquet_data))        metadata = {

        dashboard_data = {

            'update_time': datetime.now().isoformat(),                    all_stocks.append(df)

            'market_date': end_date.isoformat(),

            'top_gainers': top_gainers.to_dict('records'),            except Exception as e:            'pipeline_name': 'gold_market_features',import jsonLayer 3 - SERVING: Pre-aggregated cache for BI dashboardsfrom airflow.utils.trigger_rule import TriggerRule

            'top_losers': top_losers.to_dict('records'),

            'market_stats': {                logging.error(f"Error reading {file_key}: {e}")

                'total_tickers': len(latest_data),

                'avg_rsi': float(latest_data['RSI_14'].mean()) if 'RSI_14' in latest_data.columns else None,                continue            'layer': 'gold',

                'avg_volatility': float(latest_data['volatility_7d'].mean()) if 'volatility_7d' in latest_data.columns else None

            }        

        }

                if not all_stocks:            'execution_date': date_strimport os

        serving_prefix = f'gold/serving/market_dashboard/partition_date={partition_date_str}/'

        dashboard_key = f'{serving_prefix}dashboard_{end_date.strftime("%Y%m%d")}.json'            logging.warning("No stock data in date range")

        

        s3_hook.load_string(json.dumps(dashboard_data, indent=2, default=str), key=dashboard_key, bucket_name=S3_BUCKET, replace=True)            return        }

        

        log_pipeline_success('gold_layer', 'create_serving_cache', 1)        

        logging.info(f"Serving cache created")

                # Combine all stocks        import pandas as pd  - market_dashboard, sentiment_features, macro_features, risk_metricsfrom airflow.utils.dates import days_ago

    except Exception as e:

        log_pipeline_error('gold_layer', 'create_serving_cache', str(e))        stocks_df = pd.concat(all_stocks, ignore_index=True)

        raise

                log_pipeline_start(logger, metadata)



def track_pipeline_metadata(**context):        # Calculate technical indicators by ticker

    execution_date = context['execution_date']

    log_pipeline_start('gold_layer', 'track_pipeline_metadata', execution_date)        results = []        import numpy as np

    

    try:        for ticker in stocks_df['ticker'].unique():

        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)

        end_date = execution_date.date()            ticker_df = stocks_df[stocks_df['ticker'] == ticker].copy()        s3_hook = S3Hook(aws_conn_id='aws_default')

        

        pipeline_metadata = {            ticker_df = calculate_technical_indicators(ticker_df)

            'run_id': context['dag_run'].run_id,

            'execution_date': execution_date.isoformat(),            results.append(ticker_df)        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')import ioimport logging

            'dag_id': 'gold_layer_pipeline',

            'start_time': datetime.now().isoformat(),        

            'source_layers': ['silver/stocks', 'silver/news'],

            'transformations': ['calculate_technical_indicators', 'aggregate_sentiment', 'create_serving_cache'],        market_features_df = pd.concat(results, ignore_index=True)        

            'gold_outputs': {

                'analytics/market_features': f'partition_date={end_date.strftime("%Y-%m-%d")}',        

                'sentiment_analysis': f'partition_date={end_date.strftime("%Y-%m-%d")}',

                'serving/market_dashboard': f'partition_date={end_date.strftime("%Y-%m-%d")}'        # Write to Gold analytics layer with partitioning        # Read last 30 days for MA calculationfrom enhanced_logger import log_pipeline_start, log_pipeline_success, log_pipeline_error

            }

        }        partition_date_str = end_date.strftime('%Y-%m-%d')

        

        partition_date_str = end_date.strftime('%Y-%m-%d')        gold_prefix = f'gold/analytics/market_features/partition_date={partition_date_str}/'        all_stocks = []

        metadata_prefix = f'gold/metadata/pipeline_runs/partition_date={partition_date_str}/'

        metadata_key = f'{metadata_prefix}run_{context["dag_run"].run_id}.json'        

        

        s3_hook.load_string(json.dumps(pipeline_metadata, indent=2), key=metadata_key, bucket_name=S3_BUCKET, replace=True)        # Save as Parquet        for i in range(30):Layer 4 - METADATA: Pipeline lineage and quality trackingimport os

        

        log_pipeline_success('gold_layer', 'track_pipeline_metadata', 1)        parquet_buffer = BytesIO()

        logging.info(f"Pipeline metadata tracked")

                market_features_df.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)            past_date = (execution_date - timedelta(days=i)).strftime('%Y-%m-%d')

    except Exception as e:

        log_pipeline_error('gold_layer', 'track_pipeline_metadata', str(e))        parquet_buffer.seek(0)

        raise

                    stock_key = f"silver/stocks/partition_date={past_date}/stock_data.parquet"# Default arguments



task_market_features = PythonOperator(        s3_key = f'{gold_prefix}market_features_{end_date.strftime("%Y%m%d")}.parquet'

    task_id='create_market_features',

    python_callable=create_market_features,        s3_hook.load_bytes(            

    dag=dag

)            parquet_buffer.read(),



task_sentiment_analysis = PythonOperator(            key=s3_key,            try:default_args = {  - pipeline_runs: Execution tracking with lineageimport json

    task_id='create_sentiment_analysis',

    python_callable=create_sentiment_analysis,            bucket_name=S3_BUCKET,

    dag=dag

)            replace=True                obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=stock_key)



task_serving_cache = PythonOperator(        )

    task_id='create_serving_cache',

    python_callable=create_serving_cache,                        df_day = pd.read_parquet(io.BytesIO(obj['Body'].read()))    'owner': 'finance_portfolio',

    dag=dag

)        # Save metadata



task_pipeline_metadata = PythonOperator(        metadata = {                all_stocks.append(df_day)

    task_id='track_pipeline_metadata',

    python_callable=track_pipeline_metadata,            'execution_date': execution_date.isoformat(),

    dag=dag

)            'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()},            except:    'depends_on_past': False,  - quality_metrics: Data quality per tableimport pandas as pd



[task_market_features, task_sentiment_analysis] >> task_serving_cache >> task_pipeline_metadata            'records_processed': len(market_features_df),


            'tickers_count': market_features_df['ticker'].nunique(),                continue

            'features': ['MA_5', 'MA_10', 'MA_20', 'MA_30', 'RSI_14', 'volatility_7d']

        }            'start_date': datetime(2024, 1, 1),

        

        metadata_key = f'{gold_prefix}_metadata.json'        if not all_stocks:

        s3_hook.load_string(

            json.dumps(metadata, indent=2),            logger.warning(f"⚠️ No stock data found")    'email_on_failure': True,import numpy as np

            key=metadata_key,

            bucket_name=S3_BUCKET,            return {'features_created': 0}

            replace=True

        )            'email_on_retry': False,

        

        log_pipeline_success('gold_layer', 'create_market_features', len(market_features_df))        df = pd.concat(all_stocks, ignore_index=True)

        logging.info(f"Market features created: {len(market_features_df)} records, {market_features_df['ticker'].nunique()} tickers")

                df['data_date'] = pd.to_datetime(df['data_date'])    'retries': 3,Schedule: Daily at 8 AM (weekdays), after Silver layer

    except Exception as e:

        log_pipeline_error('gold_layer', 'create_market_features', str(e))        df = df.sort_values(['symbol', 'data_date'])

        raise

            'retry_delay': timedelta(minutes=5),



def create_sentiment_analysis(**context):        logger.info(f"📝 Processing {df['symbol'].nunique()} symbols")

    """

    Layer 2 - SENTIMENT_ANALYSIS: News Sentiment Aggregation            'execution_timeout': timedelta(hours=4),Dependencies: pandas, pyarrow, numpy# Import custom utilities

    Aggregate Silver news sentiment by date and source

    """        # Calculate indicators per symbol

    execution_date = context['execution_date']

    log_pipeline_start('gold_layer', 'create_sentiment_analysis', execution_date)        features = []}

    

    try:        for symbol in df['symbol'].unique():

        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)

                    df_symbol = df[df['symbol'] == symbol].copy().sort_values('data_date')"""import sys

        # Date range for last 7 days

        end_date = execution_date.date()            

        start_date = end_date - timedelta(days=7)

                    if date_str not in df_symbol['data_date'].astype(str).values:# DAG definition

        logging.info(f"Processing news from {start_date} to {end_date}")

                        continue

        # List news files in Silver layer

        silver_prefix = 'silver/news/'            dag = DAG(sys.path.append('/opt/airflow/plugins')

        all_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=silver_prefix)

                    # Moving Averages

        if not all_files:

            logging.warning("No Silver news files found")            df_symbol['MA_5'] = df_symbol['close'].rolling(5, min_periods=1).mean()    'gold_layer_pipeline',

            return

                    df_symbol['MA_10'] = df_symbol['close'].rolling(10, min_periods=1).mean()

        # Filter parquet files

        news_files = [f for f in all_files if f.endswith('.parquet') and 'partition_date=' in f]            df_symbol['MA_20'] = df_symbol['close'].rolling(20, min_periods=1).mean()    default_args=default_args,from airflow import DAGsys.path.append('/opt/airflow/utils')

        

        all_news = []            df_symbol['MA_30'] = df_symbol['close'].rolling(30, min_periods=1).mean()

        

        # Read news files                description='Gold layer analytics (4-layer architecture: analytics/sentiment/serving/metadata)',

        for file_key in news_files:

            try:            # RSI

                partition_str = file_key.split('partition_date=')[1].split('/')[0]

                partition_date = datetime.strptime(partition_str, '%Y-%m-%d').date()            delta = df_symbol['close'].diff()    schedule_interval='0 8 * * 1-5',  # 8 AM weekdaysfrom airflow.operators.python import PythonOperator# Temporarily comment out Spark imports for testing

                

                if start_date <= partition_date <= end_date:            gain = delta.where(delta > 0, 0).rolling(14, min_periods=1).mean()

                    obj = s3_hook.get_key(file_key, bucket_name=S3_BUCKET)

                    parquet_data = obj.get()['Body'].read()            loss = (-delta.where(delta < 0, 0)).rolling(14, min_periods=1).mean()    catchup=False,

                    df = pd.read_parquet(BytesIO(parquet_data))

                    all_news.append(df)            rs = gain / loss

            except Exception as e:

                logging.error(f"Error reading {file_key}: {e}")            df_symbol['RSI_14'] = 100 - (100 / (1 + rs))    tags=['gold', 'lakehouse', 'analytics'],from datetime import datetime, timedelta# from spark_utils import get_spark_manager, get_financial_processor, with_spark_session

                continue

                    

        if not all_news:

            logging.warning("No news data in date range")            # Volatility    max_active_runs=1

            return

                    df_symbol['volatility_7d'] = df_symbol['close'].rolling(7, min_periods=1).std()

        # Combine all news

        news_df = pd.concat(all_news, ignore_index=True)            )import logging

        

        # Ensure date column exists            today = df_symbol[df_symbol['data_date'].astype(str) == date_str].iloc[-1]

        if 'published_date' in news_df.columns:

            news_df['date'] = pd.to_datetime(news_df['published_date']).dt.date            

        

        # Aggregate by date and source            features.append({

        sentiment_agg = news_df.groupby(['date', 'source']).agg({

            'sentiment_score': ['mean', 'std', 'count'],                'symbol': symbol,import json# Import enhanced logging

            'title': 'count'

        }).reset_index()                'data_date': date_str,

        

        sentiment_agg.columns = ['date', 'source', 'avg_sentiment', 'sentiment_std', 'sentiment_count', 'news_count']                'close': today['close'],def create_market_features(**context):

        

        # Write to Gold sentiment_analysis layer                'volume': today['volume'],

        partition_date_str = end_date.strftime('%Y-%m-%d')

        gold_prefix = f'gold/sentiment_analysis/partition_date={partition_date_str}/'                'MA_5': round(today['MA_5'], 2) if pd.notna(today['MA_5']) else None,    """import osfrom enhanced_logger import get_enhanced_logger, log_pipeline_start, log_pipeline_success, log_pipeline_error

        

        parquet_buffer = BytesIO()                'MA_10': round(today['MA_10'], 2) if pd.notna(today['MA_10']) else None,

        sentiment_agg.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)

        parquet_buffer.seek(0)                'MA_20': round(today['MA_20'], 2) if pd.notna(today['MA_20']) else None,    Layer 1 - ANALYTICS: Create market_features table with technical indicators

        

        s3_key = f'{gold_prefix}sentiment_agg_{end_date.strftime("%Y%m%d")}.parquet'                'MA_30': round(today['MA_30'], 2) if pd.notna(today['MA_30']) else None,

        s3_hook.load_bytes(

            parquet_buffer.read(),                'RSI_14': round(today['RSI_14'], 2) if pd.notna(today['RSI_14']) else None,    Input: silver/stocks/partition_date=*/stock_data.parquetimport pandas as pd

            key=s3_key,

            bucket_name=S3_BUCKET,                'volatility_7d': round(today['volatility_7d'], 2) if pd.notna(today['volatility_7d']) else None,

            replace=True

        )                'partition_date': date_str    Output: gold/analytics/market_features/partition_date=YYYY-MM-DD/*.parquet

        

        # Metadata            })

        metadata = {

            'execution_date': execution_date.isoformat(),            """import numpy as np# Default args

            'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()},

            'aggregations': len(sentiment_agg),        df_features = pd.DataFrame(features)

            'news_processed': len(news_df),

            'sources': news_df['source'].unique().tolist() if 'source' in news_df.columns else []        logger.info(f"✅ Created {len(df_features)} features")    try:

        }

                

        metadata_key = f'{gold_prefix}_metadata.json'

        s3_hook.load_string(        # Write Parquet        from airflow.providers.amazon.aws.hooks.s3 import S3Hookimport pyarrow as padefault_args = {

            json.dumps(metadata, indent=2),

            key=metadata_key,        buffer = io.BytesIO()

            bucket_name=S3_BUCKET,

            replace=True        df_features.to_parquet(buffer, engine='pyarrow', compression='snappy', index=False)        

        )

                

        log_pipeline_success('gold_layer', 'create_sentiment_analysis', len(sentiment_agg))

        logging.info(f"Sentiment analysis created: {len(sentiment_agg)} aggregations from {len(news_df)} news")        s3_key = f"gold/analytics/market_features/partition_date={date_str}/features.parquet"        execution_date = context['execution_date']import pyarrow.parquet as pq    'owner': 'banking-portfolio',

        

    except Exception as e:        s3_hook.load_bytes(buffer.getvalue(), s3_key, bucket_name, replace=True)

        log_pipeline_error('gold_layer', 'create_sentiment_analysis', str(e))

        raise                date_str = execution_date.strftime('%Y-%m-%d')



        logger.info(f"✅ Uploaded {s3_key}")

def create_serving_cache(**context):

    """                import io    'depends_on_past': False,

    Layer 3 - SERVING: Pre-aggregated BI Cache

    Create serving datasets for dashboards and BI tools        result = {'features_created': len(df_features)}

    """

    execution_date = context['execution_date']        log_pipeline_success(logger, metadata, result)        logger = logging.getLogger(__name__)

    log_pipeline_start('gold_layer', 'create_serving_cache', execution_date)

            return result

    try:

        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)                logger.info(f"📊 Creating market features for {date_str}")from enhanced_logger import log_pipeline_start, log_pipeline_success, log_pipeline_error    'start_date': datetime(2025, 10, 16),

        end_date = execution_date.date()

        partition_date_str = end_date.strftime('%Y-%m-%d')    except Exception as e:

        

        # Read latest market features        log_pipeline_error(logger, metadata, e, {})        

        market_prefix = f'gold/analytics/market_features/partition_date={partition_date_str}/'

        market_files = s3_hook.list_keys(bucket_name=S3_BUCKET, prefix=market_prefix)        raise

        market_parquet = [f for f in market_files if f.endswith('.parquet')]

                metadata = {    'email_on_failure': False,

        if not market_parquet:

            logging.warning("No market features found for serving cache")

            return

        def create_sentiment_analysis(**context):            'pipeline_name': 'gold_market_features',

        # Read market features

        obj = s3_hook.get_key(market_parquet[0], bucket_name=S3_BUCKET)    """Layer 2: Aggregate news sentiment"""

        market_df = pd.read_parquet(BytesIO(obj.get()['Body'].read()))

            try:            'layer': 'gold',# Default arguments    'email_on_retry': False,

        # Create market dashboard cache (top gainers/losers)

        latest_data = market_df.sort_values('date').groupby('ticker').last().reset_index()        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

        latest_data['price_change_pct'] = ((latest_data['close'] - latest_data['open']) / latest_data['open'] * 100)

                            'data_type': 'analytics',

        # Top 10 gainers

        top_gainers = latest_data.nlargest(10, 'price_change_pct')[['ticker', 'close', 'price_change_pct', 'volume', 'RSI_14']]        execution_date = context['execution_date']

        

        # Top 10 losers        date_str = execution_date.strftime('%Y-%m-%d')            'execution_date': date_strdefault_args = {    'retries': int(os.getenv('MAX_RETRY_ATTEMPTS', 2)),

        top_losers = latest_data.nsmallest(10, 'price_change_pct')[['ticker', 'close', 'price_change_pct', 'volume', 'RSI_14']]

                

        # Market dashboard

        dashboard_data = {        logger = logging.getLogger(__name__)        }

            'update_time': datetime.now().isoformat(),

            'market_date': end_date.isoformat(),        logger.info(f"📰 Creating sentiment analysis for {date_str}")

            'top_gainers': top_gainers.to_dict('records'),

            'top_losers': top_losers.to_dict('records'),                    'owner': 'finance_portfolio',    'retry_delay': timedelta(minutes=5),

            'market_stats': {

                'total_tickers': len(latest_data),        metadata = {

                'avg_rsi': float(latest_data['RSI_14'].mean()) if 'RSI_14' in latest_data.columns else None,

                'avg_volatility': float(latest_data['volatility_7d'].mean()) if 'volatility_7d' in latest_data.columns else None            'pipeline_name': 'gold_sentiment_analysis',        log_pipeline_start(logger, metadata)

            }

        }            'layer': 'gold',

        

        # Write serving cache            'execution_date': date_str            'depends_on_past': False,    'execution_timeout': timedelta(hours=2),

        serving_prefix = f'gold/serving/market_dashboard/partition_date={partition_date_str}/'

        dashboard_key = f'{serving_prefix}dashboard_{end_date.strftime("%Y%m%d")}.json'        }

        

        s3_hook.load_string(                # Initialize S3

            json.dumps(dashboard_data, indent=2, default=str),

            key=dashboard_key,        log_pipeline_start(logger, metadata)

            bucket_name=S3_BUCKET,

            replace=True                s3_hook = S3Hook(aws_conn_id='aws_default')    'start_date': datetime(2024, 1, 1),}

        )

                s3_hook = S3Hook(aws_conn_id='aws_default')

        log_pipeline_success('gold_layer', 'create_serving_cache', 1)

        logging.info(f"Serving cache created: market_dashboard with {len(top_gainers)} gainers, {len(top_losers)} losers")        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')

        

    except Exception as e:        

        log_pipeline_error('gold_layer', 'create_serving_cache', str(e))

        raise        news_key = f"silver/news/partition_date={date_str}/news_cleaned.parquet"            'email_on_failure': True,



        

def track_pipeline_metadata(**context):

    """        try:        # Read Silver stocks data (last 30 days for MA calculation)

    Layer 4 - METADATA: Pipeline Lineage Tracking

    Track pipeline execution metadata and lineage            obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=news_key)

    """

    execution_date = context['execution_date']            df_news = pd.read_parquet(io.BytesIO(obj['Body'].read()))        logger.info(f"📂 Reading Silver stocks data...")    'email_on_retry': False,# DAG definition

    log_pipeline_start('gold_layer', 'track_pipeline_metadata', execution_date)

            except:

    try:

        s3_hook = S3Hook(aws_conn_id=S3_CONN_ID)            logger.warning(f"⚠️ No news data")        

        end_date = execution_date.date()

                    return {'sentiment_records': 0}

        # Create pipeline run metadata

        pipeline_metadata = {                # Get last 30 days of data for moving averages    'retries': 3,dag = DAG(

            'run_id': context['dag_run'].run_id,

            'execution_date': execution_date.isoformat(),        logger.info(f"📝 Processing {len(df_news)} news articles")

            'dag_id': 'gold_layer_pipeline',

            'start_time': datetime.now().isoformat(),                all_stocks = []

            'source_layers': ['silver/stocks', 'silver/news'],

            'transformations': [        # Simple sentiment

                'calculate_technical_indicators',

                'aggregate_sentiment',        def calc_sentiment(text):        for i in range(30):    'retry_delay': timedelta(minutes=5),    'gold_layer_pipeline',

                'create_serving_cache'

            ],            text_lower = str(text).lower()

            'gold_outputs': {

                'analytics/market_features': f'partition_date={end_date.strftime("%Y-%m-%d")}',            pos = sum(1 for w in ['tăng', 'tốt', 'lợi nhuận'] if w in text_lower)            past_date = (execution_date - timedelta(days=i)).strftime('%Y-%m-%d')

                'sentiment_analysis': f'partition_date={end_date.strftime("%Y-%m-%d")}',

                'serving/market_dashboard': f'partition_date={end_date.strftime("%Y-%m-%d")}'            neg = sum(1 for w in ['giảm', 'xấu', 'lỗ'] if w in text_lower)

            }

        }                        stock_key = f"silver/stocks/partition_date={past_date}/stock_data.parquet"    'execution_timeout': timedelta(hours=4),    default_args=default_args,

        

        # Write metadata            if pos > neg:

        partition_date_str = end_date.strftime('%Y-%m-%d')

        metadata_prefix = f'gold/metadata/pipeline_runs/partition_date={partition_date_str}/'                return 1.0, 'positive'            

        metadata_key = f'{metadata_prefix}run_{context["dag_run"].run_id}.json'

                    elif neg > pos:

        s3_hook.load_string(

            json.dumps(pipeline_metadata, indent=2),                return -1.0, 'negative'            try:}    description='Gold Layer - Analytics & ML Feature Engineering with Spark',

            key=metadata_key,

            bucket_name=S3_BUCKET,            return 0.0, 'neutral'

            replace=True

        )                        obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=stock_key)

        

        log_pipeline_success('gold_layer', 'track_pipeline_metadata', 1)        df_news[['sentiment_score', 'sentiment_label']] = df_news['content'].apply(

        logging.info(f"Pipeline metadata tracked: {metadata_key}")

                    lambda x: pd.Series(calc_sentiment(x))                df_day = pd.read_parquet(io.BytesIO(obj['Body'].read()))    schedule_interval='0 8 * * 1-5',  # 8:00 AM weekdays (after Silver DAG)

    except Exception as e:

        log_pipeline_error('gold_layer', 'track_pipeline_metadata', str(e))        )

        raise

                        all_stocks.append(df_day)



# Define tasks        # Aggregate

task_market_features = PythonOperator(

    task_id='create_market_features',        agg = df_news.groupby(['data_date', 'source']).agg({            except:# DAG definition    catchup=False,

    python_callable=create_market_features,

    dag=dag            'id': 'count',

)

            'sentiment_score': 'mean'                continue

task_sentiment_analysis = PythonOperator(

    task_id='create_sentiment_analysis',        }).reset_index()

    python_callable=create_sentiment_analysis,

    dag=dag                dag = DAG(    max_active_runs=1,

)

        agg.columns = ['data_date', 'source', 'article_count', 'avg_sentiment']

task_serving_cache = PythonOperator(

    task_id='create_serving_cache',        agg['partition_date'] = date_str        if not all_stocks:

    python_callable=create_serving_cache,

    dag=dag        

)

        logger.info(f"✅ Created {len(agg)} sentiment records")            logger.warning(f"⚠️ No stock data found for MA calculation")    'gold_layer_pipeline',    max_active_tasks=8,

task_pipeline_metadata = PythonOperator(

    task_id='track_pipeline_metadata',        

    python_callable=track_pipeline_metadata,

    dag=dag        # Write            result = {'features_created': 0, 'execution_date': date_str}

)

        buffer = io.BytesIO()

# Task dependencies

# Market features and sentiment can run in parallel        agg.to_parquet(buffer, engine='pyarrow', compression='snappy', index=False)            log_pipeline_success(logger, metadata, result)    default_args=default_args,    tags=['gold', 'analytics', 'spark', 'ml-features'],

# Serving cache depends on market features

# Metadata tracking runs last        

[task_market_features, task_sentiment_analysis] >> task_serving_cache >> task_pipeline_metadata

        s3_key = f"gold/sentiment_analysis/partition_date={date_str}/sentiment.parquet"            return result

        s3_hook.load_bytes(buffer.getvalue(), s3_key, bucket_name, replace=True)

                    description='Gold layer analytics (4-layer architecture: analytics/sentiment/serving/metadata)',)

        logger.info(f"✅ Uploaded {s3_key}")

                df = pd.concat(all_stocks, ignore_index=True)

        result = {'sentiment_records': len(agg)}

        log_pipeline_success(logger, metadata, result)        df['data_date'] = pd.to_datetime(df['data_date'])    schedule_interval='0 8 * * 1-5',  # 8 AM weekdays

        return result

                df = df.sort_values(['symbol', 'data_date'])

    except Exception as e:

        log_pipeline_error(logger, metadata, e, {})            catchup=False,def create_analytics_tables(**context):

        raise

        logger.info(f"📝 Loaded {len(df)} stock records for {df['symbol'].nunique()} symbols")



def create_serving_cache(**context):            tags=['gold', 'lakehouse', 'analytics'],    """Create business intelligence tables based on gold_layer_etl.py logic"""

    """Layer 3: Create BI cache"""

    try:        # Calculate technical indicators per symbol

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

                logger.info(f"📈 Calculating technical indicators...")    max_active_runs=1    # Initialize enhanced logger

        execution_date = context['execution_date']

        date_str = execution_date.strftime('%Y-%m-%d')        

        

        logger = logging.getLogger(__name__)        features = [])    logger = get_enhanced_logger("gold_analytics_creation", "INFO")

        logger.info(f"🎯 Creating serving cache for {date_str}")

                

        metadata = {

            'pipeline_name': 'gold_serving_cache',        for symbol in df['symbol'].unique():    

            'layer': 'gold',

            'execution_date': date_str            df_symbol = df[df['symbol'] == symbol].copy()

        }

                    df_symbol = df_symbol.sort_values('data_date')    # Start pipeline operation tracking

        log_pipeline_start(logger, metadata)

                    

        s3_hook = S3Hook(aws_conn_id='aws_default')

        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')            # Only process if we have today's datadef create_market_features(**context):    metadata = log_pipeline_start(

        

        # Read market features            if date_str not in df_symbol['data_date'].astype(str).values:

        try:

            market_key = f"gold/analytics/market_features/partition_date={date_str}/features.parquet"                continue    """        logger,

            obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=market_key)

            df_market = pd.read_parquet(io.BytesIO(obj['Body'].read()))            

        except:

            df_market = pd.DataFrame()            # Moving Averages    Layer 1 - ANALYTICS: Create market_features table with technical indicators        pipeline_name="gold_analytics_creation",

        

        if not df_market.empty:            df_symbol['MA_5'] = df_symbol['close'].rolling(window=5, min_periods=1).mean()

            # Create dashboard

            dashboard = pd.DataFrame({            df_symbol['MA_10'] = df_symbol['close'].rolling(window=10, min_periods=1).mean()    Input: silver/stocks/partition_date=*/stock_data.parquet        layer="gold",

                'data_date': [date_str],

                'total_symbols': [len(df_market)],            df_symbol['MA_20'] = df_symbol['close'].rolling(window=20, min_periods=1).mean()

                'avg_rsi': [df_market['RSI_14'].mean()],

                'avg_volatility': [df_market['volatility_7d'].mean()],            df_symbol['MA_30'] = df_symbol['close'].rolling(window=30, min_periods=1).mean()    Output: gold/analytics/market_features/partition_date=YYYY-MM-DD/*.parquet        operation="create_business_intelligence",

                'partition_date': [date_str]

            })            

            

            buffer = io.BytesIO()            # RSI (14-day)    """        dag_run_id=context.get('dag_run').run_id,

            dashboard.to_parquet(buffer, engine='pyarrow', compression='snappy', index=False)

                        delta = df_symbol['close'].diff()

            s3_key = f"gold/serving/market_dashboard/partition_date={date_str}/dashboard.parquet"

            s3_hook.load_bytes(buffer.getvalue(), s3_key, bucket_name, replace=True)            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()    try:        task_id=context.get('task_instance').task_id

            

            logger.info(f"✅ Created market dashboard: {s3_key}")            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()

        

        result = {'cache_created': not df_market.empty}            rs = gain / loss        from airflow.providers.amazon.aws.hooks.s3 import S3Hook    )

        log_pipeline_success(logger, metadata, result)

        return result            df_symbol['RSI_14'] = 100 - (100 / (1 + rs))

        

    except Exception as e:                        

        log_pipeline_error(logger, metadata, e, {})

        raise            # Volatility (7-day standard deviation)



            df_symbol['volatility_7d'] = df_symbol['close'].rolling(window=7, min_periods=1).std()        execution_date = context['execution_date']    try:

def track_pipeline_metadata(**context):

    """Layer 4: Track pipeline metadata"""            

    try:

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook            # Get today's row        date_str = execution_date.strftime('%Y-%m-%d')        execution_date = context['execution_date']

        

        execution_date = context['execution_date']            today_row = df_symbol[df_symbol['data_date'].astype(str) == date_str].iloc[-1]

        date_str = execution_date.strftime('%Y-%m-%d')

                                    date_str = execution_date.strftime('%Y-%m-%d')

        logger = logging.getLogger(__name__)

        logger.info(f"📊 Tracking metadata for {date_str}")            feature_record = {

        

        s3_hook = S3Hook(aws_conn_id='aws_default')                'symbol': symbol,        logger = logging.getLogger(__name__)        

        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')

                        'data_date': date_str,

        ti = context['task_instance']

        market_result = ti.xcom_pull(task_ids='create_market_features')                'close': today_row['close'],        logger.info(f"📊 Creating market features for {date_str}")        logger.log_progress(metadata, f"Starting analytics tables creation for {date_str}")

        sentiment_result = ti.xcom_pull(task_ids='create_sentiment_analysis')

                        'volume': today_row['volume'],

        metadata_record = {

            'run_id': context['dag_run'].run_id,                'MA_5': round(today_row['MA_5'], 2) if pd.notna(today_row['MA_5']) else None,                

            'execution_date': date_str,

            'dag_id': 'gold_layer_pipeline',                'MA_10': round(today_row['MA_10'], 2) if pd.notna(today_row['MA_10']) else None,

            'layers': {

                'analytics': market_result,                'MA_20': round(today_row['MA_20'], 2) if pd.notna(today_row['MA_20']) else None,        metadata = {        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

                'sentiment_analysis': sentiment_result

            },                'MA_30': round(today_row['MA_30'], 2) if pd.notna(today_row['MA_30']) else None,

            'status': 'SUCCESS',

            'partition_date': date_str                'RSI_14': round(today_row['RSI_14'], 2) if pd.notna(today_row['RSI_14']) else None,            'pipeline_name': 'gold_market_features',        import pandas as pd

        }

                        'volatility_7d': round(today_row['volatility_7d'], 2) if pd.notna(today_row['volatility_7d']) else None,

        df = pd.DataFrame([metadata_record])

                        'price_change': today_row.get('price_change', 0),            'layer': 'gold',        import json

        buffer = io.BytesIO()

        df.to_parquet(buffer, engine='pyarrow', compression='snappy', index=False)                'price_change_pct': today_row.get('price_change_pct', 0)

        

        s3_key = f"gold/metadata/pipeline_runs/partition_date={date_str}/metadata.parquet"            }            'data_type': 'analytics',        

        s3_hook.load_bytes(buffer.getvalue(), s3_key, bucket_name, replace=True)

                    

        logger.info(f"✅ Metadata tracked: {s3_key}")

                    features.append(feature_record)            'execution_date': date_str        # Initialize S3

        return {'metadata_tracked': True}

                

    except Exception as e:

        logger.error(f"💥 Metadata tracking failed: {str(e)}")        df_features = pd.DataFrame(features)        }        s3_hook = S3Hook(aws_conn_id='aws_default')

        raise

        



# Task definitions        logger.info(f"✅ Created features for {len(df_features)} symbols")                bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')

create_market_features_task = PythonOperator(

    task_id='create_market_features',        

    python_callable=create_market_features,

    dag=dag,        # Add partition_date        log_pipeline_start(logger, metadata)        

)

        df_features['partition_date'] = date_str

create_sentiment_task = PythonOperator(

    task_id='create_sentiment_analysis',                        results = {

    python_callable=create_sentiment_analysis,

    dag=dag,        # Write Parquet

)

        parquet_buffer = io.BytesIO()        # Initialize S3            'market_summary_created': False,

create_serving_task = PythonOperator(

    task_id='create_serving_cache',        df_features.to_parquet(

    python_callable=create_serving_cache,

    dag=dag,            parquet_buffer,        s3_hook = S3Hook(aws_conn_id='aws_default')            'stock_features_created': False,

)

            engine='pyarrow',

track_metadata_task = PythonOperator(

    task_id='track_pipeline_metadata',            compression='snappy',        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')            'news_sentiment_created': False,

    python_callable=track_pipeline_metadata,

    dag=dag,            index=False

)

        )                    'execution_date': date_str

# Dependencies: Layer 1&2 → Layer 3 → Layer 4

[create_market_features_task, create_sentiment_task] >> create_serving_task >> track_metadata_task        


        s3_key = f"gold/analytics/market_features/partition_date={date_str}/market_features.parquet"        # Read Silver stocks data (last 30 days for MA calculation)        }

        

        s3_hook.load_bytes(        logger.info(f"📂 Reading Silver stocks data...")        

            bytes_data=parquet_buffer.getvalue(),

            key=s3_key,                s3_paths = []

            bucket_name=bucket_name,

            replace=True        # Get last 30 days of data for moving averages        processed_records = 0

        )

                all_stocks = []        

        logger.info(f"✅ Uploaded {s3_key}")

                for i in range(30):        # 1. Create Market Summary from Silver stocks data

        # Metadata

        metadata_summary = {            past_date = (execution_date - timedelta(days=i)).strftime('%Y-%m-%d')        try:

            'processing_date': date_str,

            'partition_date': date_str,            stock_key = f"silver/stocks/partition_date={past_date}/stock_data.parquet"            logger.log_progress(metadata, "Creating market summary from silver stocks data")

            'total_symbols': len(df_features),

            'indicators_calculated': ['MA_5', 'MA_10', 'MA_20', 'MA_30', 'RSI_14', 'volatility_7d'],                        

            'schema_info': {

                'columns': list(df_features.columns),            try:            # Read processed stock data from Silver layer - aligned with actual structure

                'dtypes': {col: str(dtype) for col, dtype in df_features.dtypes.items()}

            },                obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=stock_key)            stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str.replace('-', '')}.csv"

            'file_info': {

                's3_key': s3_key,                df_day = pd.read_parquet(io.BytesIO(obj['Body'].read()))            

                'format': 'parquet',

                'compression': 'snappy'                all_stocks.append(df_day)            if not s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name):

            },

            '_schema_version': '2.0'            except:                # Try alternative date format

        }

                        continue                alt_stock_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"

        metadata_key = f"gold/analytics/market_features/partition_date={date_str}/_metadata.json"

        s3_hook.load_string(                        if s3_hook.check_for_key(key=alt_stock_key, bucket_name=bucket_name):

            string_data=json.dumps(metadata_summary, indent=2),

            key=metadata_key,        if not all_stocks:                    stock_file_key = alt_stock_key

            bucket_name=bucket_name,

            replace=True            logger.warning(f"⚠️ No stock data found for MA calculation")                else:

        )

                    result = {'features_created': 0, 'execution_date': date_str}                    logger.log_progress(metadata, "No stock data found for market summary in either format")

        result = {

            'features_created': len(df_features),            log_pipeline_success(logger, metadata, result)                    results['market_summary_created'] = False

            'partition_date': date_str,

            'execution_date': date_str            return result                

        }

                            if results['market_summary_created'] != False:  # Only proceed if we found data

        log_pipeline_success(logger, metadata, result)

        logger.info(f"✅ Market Features Complete: {result}")        df = pd.concat(all_stocks, ignore_index=True)                # Read silver stocks data

        

        return result        df['data_date'] = pd.to_datetime(df['data_date'])                csv_content = s3_hook.read_key(key=stock_file_key, bucket_name=bucket_name)

        

    except Exception as e:        df = df.sort_values(['symbol', 'data_date'])                stocks_df = pd.read_csv(pd.StringIO(csv_content))

        context_data = {

            'features_created': len(df_features) if 'df_features' in locals() else 0                        

        }

                logger.info(f"📝 Loaded {len(df)} stock records for {df['symbol'].nunique()} symbols")                logger.log_progress(metadata, f"Processing {len(stocks_df)} stock records for market summary",

        log_pipeline_error(logger, metadata, e, context_data)

        raise                                          stock_records=len(stocks_df))



        # Calculate technical indicators per symbol                

def create_sentiment_analysis(**context):

    """        logger.info(f"📈 Calculating technical indicators...")                # Create market summary aligned with Silver schema

    Layer 2 - SENTIMENT_ANALYSIS: Aggregate news sentiment by date/source

    Input: silver/news/partition_date=*/news_cleaned.parquet                        market_summary = {

    Output: gold/sentiment_analysis/partition_date=YYYY-MM-DD/*.parquet

    """        features = []                    'date': date_str,

    try:

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook                            'total_stocks': len(stocks_df),

        

        execution_date = context['execution_date']        for symbol in df['symbol'].unique():                    'avg_close_price': float(stocks_df['close'].mean()) if len(stocks_df) > 0 else 0,

        date_str = execution_date.strftime('%Y-%m-%d')

                    df_symbol = df[df['symbol'] == symbol].copy()                    'total_volume': int(stocks_df['volume'].sum()) if len(stocks_df) > 0 else 0,

        logger = logging.getLogger(__name__)

        logger.info(f"📰 Creating sentiment analysis for {date_str}")            df_symbol = df_symbol.sort_values('data_date')                    'avg_daily_return': float(stocks_df['daily_return'].mean() if 'daily_return' in stocks_df.columns else 0),

        

        metadata = {                                'price_gainers': len(stocks_df[stocks_df['daily_return'] > 0]) if 'daily_return' in stocks_df.columns and len(stocks_df) > 0 else 0,

            'pipeline_name': 'gold_sentiment_analysis',

            'layer': 'gold',            # Only process if we have today's data                    'price_losers': len(stocks_df[stocks_df['daily_return'] < 0]) if 'daily_return' in stocks_df.columns and len(stocks_df) > 0 else 0,

            'data_type': 'sentiment_analysis',

            'execution_date': date_str            if date_str not in df_symbol['data_date'].astype(str).values:                    'market_breadth_pct': (len(stocks_df[stocks_df['daily_return'] > 0]) / len(stocks_df) * 100) if 'daily_return' in stocks_df.columns and len(stocks_df) > 0 else 0,

        }

                        continue                    'unique_symbols': int(stocks_df['symbol'].nunique()) if 'symbol' in stocks_df.columns else len(stocks_df),

        log_pipeline_start(logger, metadata)

                                        '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'

        # Initialize S3

        s3_hook = S3Hook(aws_conn_id='aws_default')            # Moving Averages                }

        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')

                    df_symbol['MA_5'] = df_symbol['close'].rolling(window=5, min_periods=1).mean()                

        # Read Silver news data

        news_key = f"silver/news/partition_date={date_str}/news_cleaned.parquet"            df_symbol['MA_10'] = df_symbol['close'].rolling(window=10, min_periods=1).mean()                # Save market summary to Gold analytics

        

        try:            df_symbol['MA_20'] = df_symbol['close'].rolling(window=20, min_periods=1).mean()                market_summary_key = f"gold/analytics/market_summary/market_summary_{date_str.replace('-', '')}.json"

            obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=news_key)

            df_news = pd.read_parquet(io.BytesIO(obj['Body'].read()))            df_symbol['MA_30'] = df_symbol['close'].rolling(window=30, min_periods=1).mean()                s3_hook.load_string(

        except:

            logger.warning(f"⚠️ No news data found")                                string_data=json.dumps(market_summary, ensure_ascii=False, indent=2),

            result = {'sentiment_records': 0, 'execution_date': date_str}

            log_pipeline_success(logger, metadata, result)            # RSI (14-day)                    key=market_summary_key,

            return result

                    delta = df_symbol['close'].diff()                    bucket_name=bucket_name,

        logger.info(f"📝 Loaded {len(df_news)} news articles")

                    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()                    replace=True

        # Simple sentiment scoring (in production, use Vietnamese sentiment model)

        def calculate_sentiment(text):            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()                )

            """Simple sentiment scoring based on keywords"""

            text_lower = str(text).lower()            rs = gain / loss                

            

            positive_words = ['tăng', 'tốt', 'khả quan', 'lợi nhuận', 'phát triển', 'tăng trưởng']            df_symbol['RSI_14'] = 100 - (100 / (1 + rs))                results['market_summary_created'] = True

            negative_words = ['giảm', 'xấu', 'suy thoái', 'lỗ', 'khó khăn', 'rủi ro']

                                        logging.info(f"✅ Market summary created with {market_summary['total_stocks']} stocks")

            pos_count = sum(1 for word in positive_words if word in text_lower)

            neg_count = sum(1 for word in negative_words if word in text_lower)            # Volatility (7-day standard deviation)                

            

            if pos_count > neg_count:            df_symbol['volatility_7d'] = df_symbol['close'].rolling(window=7, min_periods=1).std()            else:

                return 1.0, 'positive'

            elif neg_count > pos_count:                            logging.warning(f"⚠️ No stock data found for market summary")

                return -1.0, 'negative'

            else:            # Get today's row                

                return 0.0, 'neutral'

                    today_row = df_symbol[df_symbol['data_date'].astype(str) == date_str].iloc[-1]        except Exception as e:

        # Calculate sentiment for each article

        df_news[['sentiment_score', 'sentiment_label']] = df_news['content'].apply(                        logging.error(f"❌ Market summary creation failed: {str(e)}")

            lambda x: pd.Series(calculate_sentiment(x))

        )            feature_record = {        

        

        # Aggregate by date and source                'symbol': symbol,        # 2. Create Stock Features for ML aligned with Silver schema

        sentiment_agg = df_news.groupby(['data_date', 'source']).agg({

            'id': 'count',                'data_date': date_str,        try:

            'sentiment_score': 'mean',

            'sentiment_label': lambda x: x.value_counts().to_dict()                'close': today_row['close'],            if results['market_summary_created']:

        }).reset_index()

                        'volume': today_row['volume'],                # Use existing stocks_df if market summary was created

        sentiment_agg.columns = ['data_date', 'source', 'article_count', 'avg_sentiment', 'sentiment_distribution']

                        'MA_5': round(today_row['MA_5'], 2) if pd.notna(today_row['MA_5']) else None,                if 'stocks_df' in locals() and not stocks_df.empty:

        # Count sentiment labels

        def count_sentiments(dist_dict):                'MA_10': round(today_row['MA_10'], 2) if pd.notna(today_row['MA_10']) else None,                    # Create ML-ready features using actual Silver schema

            return {

                'positive': dist_dict.get('positive', 0),                'MA_20': round(today_row['MA_20'], 2) if pd.notna(today_row['MA_20']) else None,                    ml_features = stocks_df.copy()

                'negative': dist_dict.get('negative', 0),

                'neutral': dist_dict.get('neutral', 0)                'MA_30': round(today_row['MA_30'], 2) if pd.notna(today_row['MA_30']) else None,                    

            }

                        'RSI_14': round(today_row['RSI_14'], 2) if pd.notna(today_row['RSI_14']) else None,                    # Ensure we have the required columns from Silver

        sentiment_agg['sentiment_counts'] = sentiment_agg['sentiment_distribution'].apply(count_sentiments)

        sentiment_agg = sentiment_agg.drop('sentiment_distribution', axis=1)                'volatility_7d': round(today_row['volatility_7d'], 2) if pd.notna(today_row['volatility_7d']) else None,                    if 'symbol' in ml_features.columns:

        

        # Add partition_date                'price_change': today_row.get('price_change', 0),                        ml_features['ticker'] = ml_features['symbol']  # Standardize naming

        sentiment_agg['partition_date'] = date_str

                        'price_change_pct': today_row.get('price_change_pct', 0)                    

        logger.info(f"✅ Created sentiment analysis for {len(sentiment_agg)} source-date combinations")

                    }                    # Price-based features using actual Silver columns

        # Write Parquet

        parquet_buffer = io.BytesIO()                                if all(col in ml_features.columns for col in ['close', 'open']):

        sentiment_agg.to_parquet(

            parquet_buffer,            features.append(feature_record)                        ml_features['price_change_pct'] = (ml_features['close'] - ml_features['open']) / ml_features['open']

            engine='pyarrow',

            compression='snappy',                            

            index=False

        )        df_features = pd.DataFrame(features)                    if all(col in ml_features.columns for col in ['high', 'low']):

        

        s3_key = f"gold/sentiment_analysis/partition_date={date_str}/sentiment_aggregated.parquet"                                ml_features['daily_range_pct'] = (ml_features['high'] - ml_features['low']) / ml_features['low']

        

        s3_hook.load_bytes(        logger.info(f"✅ Created features for {len(df_features)} symbols")                    

            bytes_data=parquet_buffer.getvalue(),

            key=s3_key,                            # Volume features

            bucket_name=bucket_name,

            replace=True        # Add partition_date                    if 'volume' in ml_features.columns:

        )

                df_features['partition_date'] = date_str                        ml_features['volume_log'] = np.log1p(ml_features['volume'])

        logger.info(f"✅ Uploaded {s3_key}")

                                        ml_features['volume_scaled'] = (ml_features['volume'] - ml_features['volume'].mean()) / ml_features['volume'].std()

        # Metadata

        metadata_summary = {        # Write Parquet                    

            'processing_date': date_str,

            'partition_date': date_str,        parquet_buffer = io.BytesIO()                    # Technical indicators from Silver (if available)

            'total_records': len(sentiment_agg),

            'total_articles_processed': int(df_news['id'].nunique()),        df_features.to_parquet(                    tech_columns = ['MA_5', 'MA_20', 'RSI', 'MACD', 'BB_position']

            'avg_sentiment_overall': float(df_news['sentiment_score'].mean()),

            'file_info': {            parquet_buffer,                    for col in tech_columns:

                's3_key': s3_key,

                'format': 'parquet',            engine='pyarrow',                        if col not in ml_features.columns:

                'compression': 'snappy'

            },            compression='snappy',                            ml_features[col] = 0  # Default values if not available

            '_schema_version': '2.0'

        }            index=False                    

        

        metadata_key = f"gold/sentiment_analysis/partition_date={date_str}/_metadata.json"        )                    # Banking sector classification

        s3_hook.load_string(

            string_data=json.dumps(metadata_summary, indent=2),                            big4_banks = ['VCB', 'BID', 'CTG', 'AGR']

            key=metadata_key,

            bucket_name=bucket_name,        s3_key = f"gold/analytics/market_features/partition_date={date_str}/market_features.parquet"                    tier1_banks = ['VPB', 'TCB', 'MBB', 'STB', 'HDB', 'ACB']

            replace=True

        )                            

        

        result = {        s3_hook.load_bytes(                    def classify_bank_tier(symbol):

            'sentiment_records': len(sentiment_agg),

            'articles_processed': int(df_news['id'].nunique()),            bytes_data=parquet_buffer.getvalue(),                        symbol = str(symbol).upper()

            'partition_date': date_str,

            'execution_date': date_str            key=s3_key,                        if symbol in big4_banks:

        }

                    bucket_name=bucket_name,                            return 'BIG_4'

        log_pipeline_success(logger, metadata, result)

        logger.info(f"✅ Sentiment Analysis Complete: {result}")            replace=True                        elif symbol in tier1_banks:

        

        return result        )                            return 'TIER_1'

        

    except Exception as e:                                else:

        context_data = {

            'records_created': len(sentiment_agg) if 'sentiment_agg' in locals() else 0        logger.info(f"✅ Uploaded {s3_key}")                            return 'TIER_2'

        }

                                    

        log_pipeline_error(logger, metadata, e, context_data)

        raise        # Metadata                    symbol_col = 'symbol' if 'symbol' in ml_features.columns else 'ticker'



        metadata_summary = {                    ml_features['bank_tier'] = ml_features[symbol_col].apply(classify_bank_tier)

def create_serving_cache(**context):

    """            'processing_date': date_str,                    

    Layer 3 - SERVING: Create pre-aggregated cache for BI dashboards

    Input: gold/analytics/*, gold/sentiment_analysis/*            'partition_date': date_str,                    # Select final ML feature columns

    Output: gold/serving/*/partition_date=YYYY-MM-DD/*.parquet

    """            'total_symbols': len(df_features),                    feature_columns = ['symbol', 'date', 'close', 'volume', 'bank_tier']

    try:

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook            'indicators_calculated': ['MA_5', 'MA_10', 'MA_20', 'MA_30', 'RSI_14', 'volatility_7d'],                    if 'daily_return' in ml_features.columns:

        

        execution_date = context['execution_date']            'schema_info': {                        feature_columns.append('daily_return')

        date_str = execution_date.strftime('%Y-%m-%d')

                        'columns': list(df_features.columns),                    if 'price_change_pct' in ml_features.columns:

        logger = logging.getLogger(__name__)

        logger.info(f"🎯 Creating serving cache for {date_str}")                'dtypes': {col: str(dtype) for col, dtype in df_features.dtypes.items()}                        feature_columns.append('price_change_pct')

        

        metadata = {            },                    if 'volume_log' in ml_features.columns:

            'pipeline_name': 'gold_serving_cache',

            'layer': 'gold',            'file_info': {                        feature_columns.append('volume_log')

            'data_type': 'serving',

            'execution_date': date_str                's3_key': s3_key,                    

        }

                        'format': 'parquet',                    # Add technical indicators

        log_pipeline_start(logger, metadata)

                        'compression': 'snappy'                    feature_columns.extend([col for col in tech_columns if col in ml_features.columns])

        # Initialize S3

        s3_hook = S3Hook(aws_conn_id='aws_default')            },                    

        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')

                    '_schema_version': '2.0'                    final_ml_features = ml_features[feature_columns].copy()

        # Read market features

        try:        }                    

            market_key = f"gold/analytics/market_features/partition_date={date_str}/market_features.parquet"

            obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=market_key)                            # Save ML features to Gold serving

            df_market = pd.read_parquet(io.BytesIO(obj['Body'].read()))

        except:        metadata_key = f"gold/analytics/market_features/partition_date={date_str}/_metadata.json"                    ml_features_csv = final_ml_features.to_csv(index=False)

            df_market = pd.DataFrame()

                s3_hook.load_string(                    ml_features_key = f"gold/serving/ml_features/ml_features_{date_str.replace('-', '')}.csv"

        # Read sentiment analysis

        try:            string_data=json.dumps(metadata_summary, indent=2),                s3_hook.load_string(

            sentiment_key = f"gold/sentiment_analysis/partition_date={date_str}/sentiment_aggregated.parquet"

            obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=sentiment_key)            key=metadata_key,                    string_data=ml_features_csv,

            df_sentiment = pd.read_parquet(io.BytesIO(obj['Body'].read()))

        except:            bucket_name=bucket_name,                    key=ml_features_key,

            df_sentiment = pd.DataFrame()

                    replace=True                    bucket_name=bucket_name,

        # Create market dashboard (top movers, volume leaders)

        if not df_market.empty:        )                    replace=True

            market_dashboard = pd.DataFrame({

                'data_date': [date_str],                        )

                'total_symbols': [len(df_market)],

                'avg_rsi': [df_market['RSI_14'].mean()],        result = {                

                'avg_volatility': [df_market['volatility_7d'].mean()],

                'top_gainers': [df_market.nlargest(10, 'price_change_pct')['symbol'].tolist()],            'features_created': len(df_features),                results['stock_features_created'] = True

                'top_losers': [df_market.nsmallest(10, 'price_change_pct')['symbol'].tolist()],

                'high_volume': [df_market.nlargest(10, 'volume')['symbol'].tolist()],            'partition_date': date_str,                logging.info(f"✅ ML features created for {len(stocks_df)} stocks")

                'partition_date': [date_str]

            })            'execution_date': date_str                

            

            # Write market dashboard        }        except Exception as e:

            parquet_buffer = io.BytesIO()

            market_dashboard.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)                    logging.error(f"❌ Stock features creation failed: {str(e)}")

            

            s3_key = f"gold/serving/market_dashboard/partition_date={date_str}/dashboard.parquet"        log_pipeline_success(logger, metadata, result)        

            s3_hook.load_bytes(bytes_data=parquet_buffer.getvalue(), key=s3_key, bucket_name=bucket_name, replace=True)

                    logger.info(f"✅ Market Features Complete: {result}")        # 3. Create News Sentiment Analytics aligned with Silver schema

            logger.info(f"✅ Market dashboard created: {s3_key}")

                        try:

        # Create sentiment features (for ML models)

        if not df_sentiment.empty:        return result            news_file_key = f"silver/news/processed/clean_news_{date_str.replace('-', '')}.csv"

            sentiment_features = df_sentiment[['data_date', 'source', 'avg_sentiment', 'article_count']].copy()

            sentiment_features['partition_date'] = date_str                    

            

            parquet_buffer = io.BytesIO()    except Exception as e:            # Try alternative date format

            sentiment_features.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)

                    context_data = {            if not s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name):

            s3_key = f"gold/serving/sentiment_features/partition_date={date_str}/features.parquet"

            s3_hook.load_bytes(bytes_data=parquet_buffer.getvalue(), key=s3_key, bucket_name=bucket_name, replace=True)            'features_created': len(df_features) if 'df_features' in locals() else 0                alt_news_key = f"silver/news/processed/clean_news_{date_str}.csv"

            

            logger.info(f"✅ Sentiment features created: {s3_key}")        }                if s3_hook.check_for_key(key=alt_news_key, bucket_name=bucket_name):

        

        result = {                            news_file_key = alt_news_key

            'market_dashboard_created': not df_market.empty,

            'sentiment_features_created': not df_sentiment.empty,        log_pipeline_error(logger, metadata, e, context_data)            

            'partition_date': date_str,

            'execution_date': date_str        raise            if s3_hook.check_for_key(key=news_file_key, bucket_name=bucket_name):

        }

                        # Read silver news data

        log_pipeline_success(logger, metadata, result)

        logger.info(f"✅ Serving Cache Complete: {result}")                csv_content = s3_hook.read_key(key=news_file_key, bucket_name=bucket_name)

        

        return resultdef create_sentiment_analysis(**context):                news_df = pd.read_csv(pd.StringIO(csv_content))

        

    except Exception as e:    """                

        context_data = {}

        log_pipeline_error(logger, metadata, e, context_data)    Layer 2 - SENTIMENT_ANALYSIS: Aggregate news sentiment by date/source                logging.info(f"📰 Processing {len(news_df)} news articles for sentiment analytics")

        raise

    Input: silver/news/partition_date=*/news_cleaned.parquet                



def track_pipeline_metadata(**context):    Output: gold/sentiment_analysis/partition_date=YYYY-MM-DD/*.parquet                # Create sentiment analytics using actual Silver schema

    """

    Layer 4 - METADATA: Track pipeline execution lineage and quality    """                sentiment_analytics = {

    Output: gold/metadata/pipeline_runs/partition_date=YYYY-MM-DD/*.parquet

    """    try:                    'date': date_str,

    try:

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook        from airflow.providers.amazon.aws.hooks.s3 import S3Hook                    'total_articles': len(news_df),

        

        execution_date = context['execution_date']                            'sentiment_distribution': {},

        date_str = execution_date.strftime('%Y-%m-%d')

                execution_date = context['execution_date']                    'topic_distribution': {},

        logger = logging.getLogger(__name__)

        logger.info(f"📊 Tracking pipeline metadata for {date_str}")        date_str = execution_date.strftime('%Y-%m-%d')                    'avg_content_length': 0,

        

        # Initialize S3                            'banking_articles': 0,

        s3_hook = S3Hook(aws_conn_id='aws_default')

        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')        logger = logging.getLogger(__name__)                    'positive_sentiment_ratio': 0,

        

        # Get task results from XCom        logger.info(f"📰 Creating sentiment analysis for {date_str}")                    '_created_at_utc': pd.Timestamp.utcnow().isoformat() + 'Z'

        ti = context['task_instance']

        market_result = ti.xcom_pull(task_ids='create_market_features')                        }

        sentiment_result = ti.xcom_pull(task_ids='create_sentiment_analysis')

        serving_result = ti.xcom_pull(task_ids='create_serving_cache')        metadata = {                

        

        # Create pipeline run record            'pipeline_name': 'gold_sentiment_analysis',                # Handle sentiment columns based on actual Silver output

        pipeline_run = {

            'run_id': context['dag_run'].run_id,            'layer': 'gold',                if 'sentiment_basic' in news_df.columns:

            'execution_date': date_str,

            'dag_id': 'gold_layer_pipeline',            'data_type': 'sentiment_analysis',                    sentiment_analytics['sentiment_distribution'] = news_df['sentiment_basic'].value_counts().to_dict()

            'pipeline_layers': {

                'analytics': {            'execution_date': date_str                    positive_count = len(news_df[news_df['sentiment_basic'] == 'POSITIVE'])

                    'market_features_created': market_result.get('features_created', 0) if market_result else 0

                },        }                    sentiment_analytics['positive_sentiment_ratio'] = (positive_count / len(news_df) * 100) if len(news_df) > 0 else 0

                'sentiment_analysis': {

                    'sentiment_records': sentiment_result.get('sentiment_records', 0) if sentiment_result else 0                        elif 'sentiment_score' in news_df.columns:

                },

                'serving': {        log_pipeline_start(logger, metadata)                    # Create basic sentiment from scores

                    'market_dashboard': serving_result.get('market_dashboard_created', False) if serving_result else False,

                    'sentiment_features': serving_result.get('sentiment_features_created', False) if serving_result else False                            news_df['sentiment_basic'] = news_df['sentiment_score'].apply(

                }

            },        # Initialize S3                        lambda x: 'POSITIVE' if x > 0.1 else ('NEGATIVE' if x < -0.1 else 'NEUTRAL')

            'source_layers': ['bronze', 'silver'],

            'transformations': ['technical_indicators', 'sentiment_analysis', 'pre_aggregation'],        s3_hook = S3Hook(aws_conn_id='aws_default')                    )

            'status': 'SUCCESS',

            'partition_date': date_str        bucket_name = os.getenv('S3_BUCKET', 'bankanalystportfolio')                    sentiment_analytics['sentiment_distribution'] = news_df['sentiment_basic'].value_counts().to_dict()

        }

                                    positive_count = len(news_df[news_df['sentiment_basic'] == 'POSITIVE'])

        df_metadata = pd.DataFrame([pipeline_run])

                # Read Silver news data                    sentiment_analytics['positive_sentiment_ratio'] = (positive_count / len(news_df) * 100) if len(news_df) > 0 else 0

        # Write metadata

        parquet_buffer = io.BytesIO()        news_key = f"silver/news/partition_date={date_str}/news_cleaned.parquet"                

        df_metadata.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=False)

                                # Handle topic/category columns

        s3_key = f"gold/metadata/pipeline_runs/partition_date={date_str}/run_metadata.parquet"

        s3_hook.load_bytes(bytes_data=parquet_buffer.getvalue(), key=s3_key, bucket_name=bucket_name, replace=True)        try:                if 'topic_category' in news_df.columns:

        

        logger.info(f"✅ Pipeline metadata tracked: {s3_key}")            obj = s3_hook.get_conn().get_object(Bucket=bucket_name, Key=news_key)                    sentiment_analytics['topic_distribution'] = news_df['topic_category'].value_counts().to_dict()

        

        return {'metadata_tracked': True, 'execution_date': date_str}            df_news = pd.read_parquet(io.BytesIO(obj['Body'].read()))                    sentiment_analytics['banking_articles'] = len(news_df[news_df['topic_category'] == 'BANKING'])

        

    except Exception as e:        except:                elif 'category' in news_df.columns:

        logger.error(f"💥 Metadata tracking failed: {str(e)}")

        raise            logger.warning(f"⚠️ No news data found")                    sentiment_analytics['topic_distribution'] = news_df['category'].value_counts().to_dict()



            result = {'sentiment_records': 0, 'execution_date': date_str}                    sentiment_analytics['banking_articles'] = len(news_df[news_df['category'].str.contains('BANK', case=False, na=False)])

# Task definitions

create_market_features_task = PythonOperator(            log_pipeline_success(logger, metadata, result)                

    task_id='create_market_features',

    python_callable=create_market_features,            return result                # Handle content length

    dag=dag,

)                        if 'content_length' in news_df.columns:



create_sentiment_task = PythonOperator(        logger.info(f"📝 Loaded {len(df_news)} news articles")                    sentiment_analytics['avg_content_length'] = float(news_df['content_length'].mean())

    task_id='create_sentiment_analysis',

    python_callable=create_sentiment_analysis,                        elif 'combined_text' in news_df.columns:

    dag=dag,

)        # Simple sentiment scoring (in production, use Vietnamese sentiment model)                    news_df['content_length'] = news_df['combined_text'].str.len()



create_serving_task = PythonOperator(        def calculate_sentiment(text):                    sentiment_analytics['avg_content_length'] = float(news_df['content_length'].mean())

    task_id='create_serving_cache',

    python_callable=create_serving_cache,            """Simple sentiment scoring based on keywords"""                elif 'title' in news_df.columns:

    dag=dag,

)            text_lower = str(text).lower()                    news_df['content_length'] = news_df['title'].str.len()



track_metadata_task = PythonOperator(                                sentiment_analytics['avg_content_length'] = float(news_df['content_length'].mean())

    task_id='track_pipeline_metadata',

    python_callable=track_pipeline_metadata,            positive_words = ['tăng', 'tốt', 'khả quan', 'lợi nhuận', 'phát triển', 'tăng trưởng']                

    dag=dag,

)            negative_words = ['giảm', 'xấu', 'suy thoái', 'lỗ', 'khó khăn', 'rủi ro']                # Save sentiment analytics with S3 logging



# Task dependencies                            sentiment_key = f"gold/analytics/sentiment_analysis/news_sentiment_{date_str.replace('-', '')}.json"

# Layer 1 & 2 run in parallel → Layer 3 → Layer 4

[create_market_features_task, create_sentiment_task] >> create_serving_task >> track_metadata_task            pos_count = sum(1 for word in positive_words if word in text_lower)                logger.log_s3_operation(metadata, "write", sentiment_key, "analytics_json")


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
