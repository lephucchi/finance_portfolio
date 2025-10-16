# ===============================================================
# 🪙 ETL: CHUYỂN DỮ LIỆU TỪ BRONZE → SILVER (KAGGLE ENVIRONMENT)
# Version: v4.0 (Complete Rewrite - Based on Actual Bronze Structure)
# ===============================================================

import boto3
import pandas as pd
import numpy as np
import io, json, os, time
from datetime import datetime, timezone
import warnings
from typing import Dict, List, Optional, Tuple
import glob

warnings.filterwarnings('ignore')

# Import for Kaggle secrets
from kaggle_secrets import UserSecretsClient
try:
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    class ClientError(Exception):
        pass
    class NoCredentialsError(Exception):
        pass

# ====== KAGGLE ENVIRONMENT CONFIG ======
KAGGLE_WORKING_DIR = "/kaggle/working"
OUTPUT_PROCESSED_DIR = os.path.join(KAGGLE_WORKING_DIR, "silver_processed")
OUTPUT_META_DIR = os.path.join(KAGGLE_WORKING_DIR, "silver_metadata")

# Create directories
os.makedirs(OUTPUT_PROCESSED_DIR, exist_ok=True)
os.makedirs(OUTPUT_META_DIR, exist_ok=True)

# S3 Configuration - Based on actual Bronze structure
S3_BUCKET = "bankanalystportfolio"
S3_BRONZE_STOCKS = "bronze/stocks"
S3_BRONZE_NEWS = "bronze/news"
S3_BRONZE_OTHERS = "bronze/others"
S3_SILVER_BASE = "silver"

# ====== S3 AND AWS CONFIGURATION ======
def get_s3_client() -> Optional[boto3.client]:
    """Khởi tạo S3 client với AWS credentials từ Kaggle secrets."""
    try:
        user_secrets = UserSecretsClient()
        aws_key_id = user_secrets.get_secret("AWS_ACCESS_KEY_ID")
        aws_secret = user_secrets.get_secret("AWS_SECRET_ACCESS_KEY")
        aws_region = user_secrets.get_secret("AWS_REGION")
        
        if not all([aws_key_id, aws_secret, aws_region]):
            debug_print("❌ Missing AWS credentials in Kaggle secrets", "ERROR")
            return None
            
        config = boto3.session.Config(
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            read_timeout=60,
            connect_timeout=30
        )
        
        client = boto3.client(
            's3', 
            aws_access_key_id=aws_key_id, 
            aws_secret_access_key=aws_secret, 
            region_name=aws_region,
            config=config
        )
        
        # Test connection
        client.head_bucket(Bucket=S3_BUCKET)
        debug_print(f"✅ S3 client initialized successfully")
        return client
        
    except Exception as e:
        debug_print(f"❌ Error initializing S3 client: {e}", "ERROR")
        return None

def debug_print(message: str, level: str = "INFO"):
    """Enhanced logging với timestamps."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}", flush=True)

# ====== UTILITY FUNCTIONS ======
def read_csv_from_s3(s3_client: boto3.client, bucket: str, key: str) -> Optional[pd.DataFrame]:
    """Đọc file CSV từ S3."""
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        return pd.read_csv(io.BytesIO(obj['Body'].read()))
    except Exception as e:
        debug_print(f"❌ Error reading {key}: {e}", "ERROR")
        return None

def read_json_from_s3(s3_client: boto3.client, bucket: str, key: str) -> Optional[dict]:
    """Đọc file JSON từ S3."""
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        return json.loads(obj['Body'].read().decode('utf-8'))
    except Exception as e:
        debug_print(f"❌ Error reading JSON {key}: {e}", "ERROR")
        return None

def list_s3_files(s3_client: boto3.client, bucket: str, prefix: str) -> List[str]:
    """Liệt kê files trong S3 với prefix cụ thể."""
    try:
        files = []
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            if 'Contents' in page:
                files.extend([obj['Key'] for obj in page['Contents']])
        return files
    except Exception as e:
        debug_print(f"❌ Error listing files with prefix {prefix}: {e}", "ERROR")
        return []

def upload_to_s3(s3_client: boto3.client, bucket: str, content: str, key: str, content_type: str = 'text/csv') -> bool:
    """Upload content lên S3."""
    try:
        if isinstance(content, bytes):
            body = content
        else:
            body = content.encode('utf-8') if isinstance(content, str) else content
            
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType=content_type
        )
        debug_print(f"✅ Uploaded: {key}")
        return True
    except Exception as e:
        debug_print(f"❌ Upload failed for {key}: {e}", "ERROR")
        return False

# ====== TECHNICAL INDICATORS CALCULATION ======
def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Tính toán các chỉ số kỹ thuật cần thiết cho phân tích."""
    try:
        df = df.copy()
        
        # Ensure we have required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            debug_print(f"⚠️ Missing columns for technical indicators: {missing_cols}", "WARNING")
            return df
        
        # Sort by symbol and date if available
        if 'symbol' in df.columns and 'date' in df.columns:
            df = df.sort_values(['symbol', 'date']).reset_index(drop=True)
        elif 'date' in df.columns:
            df = df.sort_values('date').reset_index(drop=True)
        
        # Group by symbol để tính toán cho từng mã
        def calculate_for_symbol(symbol_df):
            symbol_df = symbol_df.sort_values('date').reset_index(drop=True) if 'date' in symbol_df.columns else symbol_df
            
            # 1. Moving Averages
            symbol_df['MA_5'] = symbol_df['close'].rolling(window=5, min_periods=1).mean()
            symbol_df['MA_10'] = symbol_df['close'].rolling(window=10, min_periods=1).mean()
            symbol_df['MA_20'] = symbol_df['close'].rolling(window=20, min_periods=1).mean()
            symbol_df['MA_50'] = symbol_df['close'].rolling(window=50, min_periods=1).mean()
            
            # 2. Exponential Moving Averages
            symbol_df['EMA_12'] = symbol_df['close'].ewm(span=12, min_periods=1).mean()
            symbol_df['EMA_26'] = symbol_df['close'].ewm(span=26, min_periods=1).mean()
            
            # 3. MACD (Moving Average Convergence Divergence)
            symbol_df['MACD'] = symbol_df['EMA_12'] - symbol_df['EMA_26']
            symbol_df['MACD_signal'] = symbol_df['MACD'].ewm(span=9, min_periods=1).mean()
            symbol_df['MACD_histogram'] = symbol_df['MACD'] - symbol_df['MACD_signal']
            
            # 4. RSI (Relative Strength Index)
            delta = symbol_df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
            rs = gain / loss.replace(0, np.nan)
            symbol_df['RSI'] = 100 - (100 / (1 + rs))
            
            # 5. Bollinger Bands
            symbol_df['BB_middle'] = symbol_df['close'].rolling(window=20, min_periods=1).mean()
            bb_std = symbol_df['close'].rolling(window=20, min_periods=1).std()
            symbol_df['BB_upper'] = symbol_df['BB_middle'] + (bb_std * 2)
            symbol_df['BB_lower'] = symbol_df['BB_middle'] - (bb_std * 2)
            symbol_df['BB_width'] = symbol_df['BB_upper'] - symbol_df['BB_lower']
            symbol_df['BB_position'] = (symbol_df['close'] - symbol_df['BB_lower']) / symbol_df['BB_width'].replace(0, np.nan)
            
            # 6. Volume indicators
            symbol_df['volume_MA_10'] = symbol_df['volume'].rolling(window=10, min_periods=1).mean()
            symbol_df['volume_ratio'] = symbol_df['volume'] / symbol_df['volume_MA_10'].replace(0, np.nan)
            
            # 7. Price change indicators
            symbol_df['price_change'] = symbol_df['close'].pct_change()
            symbol_df['price_change_5d'] = symbol_df['close'].pct_change(periods=5)
            symbol_df['price_change_10d'] = symbol_df['close'].pct_change(periods=10)
            
            # 8. Volatility (20-day rolling standard deviation)
            symbol_df['volatility_20d'] = symbol_df['price_change'].rolling(window=20, min_periods=1).std()
            
            # 9. Support and Resistance levels (based on rolling min/max)
            symbol_df['support_20d'] = symbol_df['low'].rolling(window=20, min_periods=1).min()
            symbol_df['resistance_20d'] = symbol_df['high'].rolling(window=20, min_periods=1).max()
            
            # 10. Average True Range (ATR)
            symbol_df['prev_close'] = symbol_df['close'].shift(1)
            symbol_df['true_range'] = np.maximum(
                symbol_df['high'] - symbol_df['low'],
                np.maximum(
                    abs(symbol_df['high'] - symbol_df['prev_close']),
                    abs(symbol_df['low'] - symbol_df['prev_close'])
                )
            )
            symbol_df['ATR'] = symbol_df['true_range'].rolling(window=14, min_periods=1).mean()
            symbol_df.drop(['prev_close', 'true_range'], axis=1, inplace=True, errors='ignore')
            
            return symbol_df
        
        # Apply calculations
        if 'symbol' in df.columns:
            result_dfs = []
            for symbol in df['symbol'].unique():
                symbol_data = df[df['symbol'] == symbol].copy()
                symbol_processed = calculate_for_symbol(symbol_data)
                result_dfs.append(symbol_processed)
            final_df = pd.concat(result_dfs, ignore_index=True)
        else:
            final_df = calculate_for_symbol(df)
        
        debug_print(f"✅ Technical indicators calculated")
        return final_df
        
    except Exception as e:
        debug_print(f"❌ Error calculating technical indicators: {e}", "ERROR")
        return df

def clean_and_validate_data(df: pd.DataFrame, data_type: str) -> Tuple[pd.DataFrame, Dict]:
    """Làm sạch và validate dữ liệu với logging chi tiết."""
    original_count = len(df)
    transformation_log = {
        "original_rows": original_count,
        "transformations": [],
        "final_rows": 0,
        "data_quality": {}
    }
    
    try:
        # 1. Remove duplicates
        before_duplicates = len(df)
        if data_type == "stocks":
            if 'symbol' in df.columns and 'date' in df.columns:
                df = df.drop_duplicates(subset=['symbol', 'date'], keep='last')
            else:
                df = df.drop_duplicates()
        elif data_type == "news":
            if 'id' in df.columns:
                df = df.drop_duplicates(subset=['id'], keep='first')
            else:
                df = df.drop_duplicates()
        else:
            df = df.drop_duplicates()
        
        duplicates_removed = before_duplicates - len(df)
        if duplicates_removed > 0:
            transformation_log["transformations"].append({
                "step": "remove_duplicates",
                "rows_removed": duplicates_removed,
                "remaining_rows": len(df)
            })
        
        # 2. Handle missing values
        if data_type == "stocks":
            # For stocks, drop rows missing critical fields
            critical_fields = []
            if 'symbol' in df.columns:
                critical_fields.append('symbol')
            if 'date' in df.columns:
                critical_fields.append('date')
            # Add numeric fields that exist
            for field in ['open', 'high', 'low', 'close', 'volume']:
                if field in df.columns:
                    critical_fields.append(field)
            
            if critical_fields:
                before_na = len(df)
                df = df.dropna(subset=critical_fields)
                na_removed = before_na - len(df)
                
                if na_removed > 0:
                    transformation_log["transformations"].append({
                        "step": "remove_missing_critical_data",
                        "rows_removed": na_removed,
                        "remaining_rows": len(df),
                        "critical_fields": critical_fields
                    })
            
            # Convert data types
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
            
            # Replace infinite values
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            df[numeric_columns] = df[numeric_columns].replace([np.inf, -np.inf], np.nan)
            
        elif data_type == "news":
            # For news, clean text fields
            before_na = len(df)
            if 'id' in df.columns:
                df = df.dropna(subset=['id'])
            na_removed = before_na - len(df)
            
            if na_removed > 0:
                transformation_log["transformations"].append({
                    "step": "remove_missing_id",
                    "rows_removed": na_removed,
                    "remaining_rows": len(df)
                })
            
            # Clean text fields
            text_fields = ['title', 'combined_text', 'content']
            for field in text_fields:
                if field in df.columns:
                    df[field] = df[field].astype(str).str.replace(r'<.*?>', '', regex=True)
                    df[field] = df[field].str.strip()
            
            # Clean date
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
        
        # 3. Data quality assessment
        transformation_log["data_quality"] = {
            "missing_values_by_column": df.isnull().sum().to_dict(),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024**2), 2)
        }
        
        # 4. Sort data
        if data_type == "stocks" and 'symbol' in df.columns and 'date' in df.columns:
            df = df.sort_values(['symbol', 'date'])
        elif 'date' in df.columns:
            df = df.sort_values('date')
        
        transformation_log["final_rows"] = len(df)
        transformation_log["data_reduction_percent"] = round((original_count - len(df)) / original_count * 100, 2) if original_count > 0 else 0
        
        debug_print(f"✅ {data_type} data cleaned: {original_count} → {len(df)} rows")
        return df, transformation_log
        
    except Exception as e:
        debug_print(f"❌ Error cleaning {data_type} data: {e}", "ERROR")
        transformation_log["final_rows"] = len(df)
        return df, transformation_log

# ====== SILVER LAYER PROCESSING FUNCTIONS ======
def process_stocks_data(s3_client: boto3.client, s3_bucket: str) -> bool:
    """Xử lý dữ liệu cổ phiếu từ Bronze sang Silver - Based on actual structure."""
    debug_print("📈 Processing stocks data...")
    
    try:
        # Method 1: Try to read from individual JSON files (actual structure)
        debug_print("🔍 Looking for stocks JSON files in bronze/stocks/raw/")
        
        # List all files in bronze/stocks/raw/
        bronze_files = list_s3_files(s3_client, s3_bucket, f"{S3_BRONZE_STOCKS}/raw/")
        json_files = [f for f in bronze_files if f.endswith('.json') and '/raw/' in f]
        
        debug_print(f"📊 Found {len(json_files)} JSON files in stocks bronze layer")
        
        if json_files:
            # Read JSON files and combine
            all_stock_data = []
            processed_files = 0
            
            # Limit to first 100 files to avoid timeout
            for json_file in json_files[:100]:
                try:
                    json_data = read_json_from_s3(s3_client, s3_bucket, json_file)
                    if json_data:
                        # Convert JSON to DataFrame row
                        if isinstance(json_data, dict):
                            # Extract ticker from file path: bronze/stocks/raw/VCB/VCB_2024-01-01.json
                            ticker = json_file.split('/')[-2] if '/' in json_file else 'UNKNOWN'
                            json_data['symbol'] = ticker
                            all_stock_data.append(json_data)
                            processed_files += 1
                            
                            if processed_files % 20 == 0:
                                debug_print(f"   Processed {processed_files} files...")
                except Exception as e:
                    debug_print(f"⚠️ Error reading {json_file}: {e}", "WARNING")
                    continue
            
            if all_stock_data:
                debug_print(f"✅ Successfully read {len(all_stock_data)} stock records from JSON files")
                df_stocks = pd.DataFrame(all_stock_data)
            else:
                debug_print("❌ No valid stock data found in JSON files", "ERROR")
                return False
        else:
            # Method 2: Try CSV files from index folder
            debug_print("🔍 Looking for CSV files in bronze/stocks/raw/index/")
            index_files = list_s3_files(s3_client, s3_bucket, f"{S3_BRONZE_STOCKS}/raw/index/")
            csv_files = [f for f in index_files if f.endswith('.csv')]
            
            if csv_files:
                debug_print(f"📊 Found {len(csv_files)} CSV files in index folder")
                all_dfs = []
                for csv_file in csv_files:
                    df = read_csv_from_s3(s3_client, s3_bucket, csv_file)
                    if df is not None and not df.empty:
                        # Add symbol from filename
                        symbol = csv_file.split('/')[-1].replace('.csv', '').upper()
                        df['symbol'] = symbol
                        all_dfs.append(df)
                
                if all_dfs:
                    df_stocks = pd.concat(all_dfs, ignore_index=True)
                    debug_print(f"✅ Combined {len(df_stocks)} records from CSV files")
                else:
                    debug_print("❌ No valid CSV data found", "ERROR")
                    return False
            else:
                debug_print("❌ No stocks data found in bronze layer", "ERROR")
                return False
        
        # Clean and validate data
        df_clean, transformation_log = clean_and_validate_data(df_stocks, "stocks")
        
        if df_clean.empty:
            debug_print("❌ No data remaining after cleaning", "ERROR")
            return False
        
        # Calculate technical indicators
        df_enhanced = calculate_technical_indicators(df_clean)
        
        # Generate date string
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Save CSV version
        csv_content = df_enhanced.to_csv(index=False)
        csv_key = f"{S3_SILVER_BASE}/stocks/processed/clean_stocks_{date_str}.csv"
        csv_success = upload_to_s3(s3_client, s3_bucket, csv_content, csv_key, 'text/csv')
        
        # Save Parquet version
        try:
            parquet_buffer = io.BytesIO()
            df_enhanced.to_parquet(parquet_buffer, index=False, engine='pyarrow')
            parquet_key = f"{S3_SILVER_BASE}/stocks/processed/clean_stocks_{date_str}.parquet"
            parquet_success = upload_to_s3(s3_client, s3_bucket, parquet_buffer.getvalue(), parquet_key, 'application/octet-stream')
        except ImportError:
            debug_print("⚠️ PyArrow not available, skipping Parquet format", "WARNING")
            parquet_success = True
        except Exception as e:
            debug_print(f"⚠️ Error creating Parquet: {e}", "WARNING")
            parquet_success = True
        
        # Create metadata
        stocks_metadata = {
            "dataset_info": {
                "name": "clean_stocks",
                "description": "Cleaned stock data with technical indicators",
                "rows": len(df_enhanced),
                "columns": len(df_enhanced.columns),
                "symbols_count": len(df_enhanced['symbol'].unique()) if 'symbol' in df_enhanced.columns else 0,
                "date_range": {
                    "start": str(df_enhanced['date'].min()) if 'date' in df_enhanced.columns else None,
                    "end": str(df_enhanced['date'].max()) if 'date' in df_enhanced.columns else None
                }
            },
            "schema_info": {
                "columns": list(df_enhanced.columns),
                "data_types": {col: str(dtype) for col, dtype in df_enhanced.dtypes.items()},
                "technical_indicators": [
                    "MA_5", "MA_10", "MA_20", "MA_50", "EMA_12", "EMA_26",
                    "MACD", "MACD_signal", "MACD_histogram", "RSI",
                    "BB_upper", "BB_middle", "BB_lower", "BB_width", "BB_position",
                    "volume_MA_10", "volume_ratio", "price_change", "price_change_5d", 
                    "price_change_10d", "volatility_20d", "support_20d", "resistance_20d", "ATR"
                ]
            },
            "processing_info": {
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "source_files_count": len(json_files) if json_files else len(csv_files),
                "processing_version": "4.0"
            }
        }
        
        # Upload metadata
        metadata_content = json.dumps(stocks_metadata, indent=2, ensure_ascii=False)
        metadata_key = f"{S3_SILVER_BASE}/stocks/metadata/stocks_metadata.json"
        metadata_success = upload_to_s3(s3_client, s3_bucket, metadata_content, metadata_key, 'application/json')
        
        # Upload transformation log
        transformation_content = json.dumps(transformation_log, indent=2, ensure_ascii=False)
        transformation_key = f"{S3_SILVER_BASE}/stocks/metadata/transformation_log.json"
        transformation_success = upload_to_s3(s3_client, s3_bucket, transformation_content, transformation_key, 'application/json')
        
        success = csv_success and metadata_success and transformation_success
        debug_print(f"✅ Stocks processing: {'Success' if success else 'Partial success'}")
        return success
        
    except Exception as e:
        debug_print(f"❌ Error processing stocks data: {e}", "ERROR")
        return False

def process_news_data(s3_client: boto3.client, s3_bucket: str) -> bool:
    """Xử lý dữ liệu tin tức từ Bronze sang Silver - Based on actual structure."""
    debug_print("📰 Processing news data...")
    
    try:
        # Method 1: Try to read individual JSON files
        debug_print("🔍 Looking for news JSON files in bronze/news/raw/")
        
        bronze_files = list_s3_files(s3_client, s3_bucket, f"{S3_BRONZE_NEWS}/raw/")
        json_files = [f for f in bronze_files if f.endswith('.json') and '/raw/' in f and not f.endswith('_metadata.json')]
        
        debug_print(f"📊 Found {len(json_files)} JSON files in news bronze layer")
        
        if json_files:
            # Read JSON files and combine
            all_news_data = []
            processed_files = 0
            
            # Limit to first 200 files to avoid timeout
            for json_file in json_files[:200]:
                try:
                    json_data = read_json_from_s3(s3_client, s3_bucket, json_file)
                    if json_data:
                        if isinstance(json_data, dict):
                            all_news_data.append(json_data)
                            processed_files += 1
                            
                            if processed_files % 50 == 0:
                                debug_print(f"   Processed {processed_files} files...")
                except Exception as e:
                    debug_print(f"⚠️ Error reading {json_file}: {e}", "WARNING")
                    continue
            
            if all_news_data:
                debug_print(f"✅ Successfully read {len(all_news_data)} news records from JSON files")
                df_news = pd.DataFrame(all_news_data)
            else:
                # Method 2: Try CSV file
                debug_print("🔍 Looking for CSV file in bronze/news/raw/")
                csv_files = [f for f in bronze_files if f.endswith('.csv')]
                
                if csv_files:
                    news_file = csv_files[0]  # Take first CSV
                    df_news = read_csv_from_s3(s3_client, s3_bucket, news_file)
                    if df_news is None or df_news.empty:
                        debug_print("❌ Failed to read news CSV or data is empty", "ERROR")
                        return False
                    debug_print(f"✅ Read {len(df_news)} records from CSV file")
                else:
                    debug_print("❌ No news data found in bronze layer", "ERROR")
                    return False
        else:
            # Try CSV file directly
            bronze_files = list_s3_files(s3_client, s3_bucket, f"{S3_BRONZE_NEWS}/raw/")
            csv_files = [f for f in bronze_files if f.endswith('.csv')]
            
            if csv_files:
                news_file = csv_files[0]
                df_news = read_csv_from_s3(s3_client, s3_bucket, news_file)
                if df_news is None or df_news.empty:
                    debug_print("❌ Failed to read news data or data is empty", "ERROR")
                    return False
                debug_print(f"✅ Read {len(df_news)} records from CSV file")
            else:
                debug_print("❌ No news data found in bronze layer", "ERROR")
                return False
        
        # Clean and validate data
        df_clean, transformation_log = clean_and_validate_data(df_news, "news")
        
        if df_clean.empty:
            debug_print("❌ No data remaining after cleaning", "ERROR")
            return False
        
        # Generate date string
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Save CSV version
        csv_content = df_clean.to_csv(index=False)
        csv_key = f"{S3_SILVER_BASE}/news/processed/clean_news_{date_str}.csv"
        csv_success = upload_to_s3(s3_client, s3_bucket, csv_content, csv_key, 'text/csv')
        
        # Save Parquet version
        try:
            parquet_buffer = io.BytesIO()
            df_clean.to_parquet(parquet_buffer, index=False, engine='pyarrow')
            parquet_key = f"{S3_SILVER_BASE}/news/processed/clean_news_{date_str}.parquet"
            parquet_success = upload_to_s3(s3_client, s3_bucket, parquet_buffer.getvalue(), parquet_key, 'application/octet-stream')
        except ImportError:
            debug_print("⚠️ PyArrow not available, skipping Parquet format", "WARNING")
            parquet_success = True
        except Exception as e:
            debug_print(f"⚠️ Error creating Parquet: {e}", "WARNING")
            parquet_success = True
        
        # Create metadata
        news_metadata = {
            "dataset_info": {
                "name": "clean_news",
                "description": "Cleaned news data with text processing",
                "rows": len(df_clean),
                "columns": len(df_clean.columns),
                "date_range": {
                    "start": str(df_clean['date'].min()) if 'date' in df_clean.columns else None,
                    "end": str(df_clean['date'].max()) if 'date' in df_clean.columns else None
                }
            },
            "schema_info": {
                "columns": list(df_clean.columns),
                "data_types": {col: str(dtype) for col, dtype in df_clean.dtypes.items()},
                "text_cleaning": [
                    "HTML tags removed",
                    "Text trimmed",
                    "Date normalized"
                ]
            },
            "processing_info": {
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "source_files_count": len(json_files) if json_files else 1,
                "processing_version": "4.0"
            }
        }
        
        # Upload metadata
        metadata_content = json.dumps(news_metadata, indent=2, ensure_ascii=False)
        metadata_key = f"{S3_SILVER_BASE}/news/metadata/news_metadata.json"
        metadata_success = upload_to_s3(s3_client, s3_bucket, metadata_content, metadata_key, 'application/json')
        
        # Upload schema info
        schema_info = {
            "schema_version": "1.0",
            "columns": {
                col: {
                    "type": str(df_clean[col].dtype),
                    "null_count": int(df_clean[col].isnull().sum()),
                    "unique_values": int(df_clean[col].nunique()) if df_clean[col].dtype != 'object' or len(df_clean[col].unique()) < 100 else "many"
                } for col in df_clean.columns
            },
            "table_stats": {
                "total_rows": len(df_clean),
                "total_columns": len(df_clean.columns),
                "memory_usage_mb": round(df_clean.memory_usage(deep=True).sum() / (1024**2), 2)
            }
        }
        schema_content = json.dumps(schema_info, indent=2, ensure_ascii=False)
        schema_key = f"{S3_SILVER_BASE}/news/metadata/schema_info.json"
        schema_success = upload_to_s3(s3_client, s3_bucket, schema_content, schema_key, 'application/json')
        
        # Upload transformation log
        transformation_content = json.dumps(transformation_log, indent=2, ensure_ascii=False)
        transformation_key = f"{S3_SILVER_BASE}/news/metadata/transformation_log.json"
        transformation_success = upload_to_s3(s3_client, s3_bucket, transformation_content, transformation_key, 'application/json')
        
        success = csv_success and metadata_success and schema_success and transformation_success
        debug_print(f"✅ News processing: {'Success' if success else 'Partial success'}")
        return success
        
    except Exception as e:
        debug_print(f"❌ Error processing news data: {e}", "ERROR")
        return False

def process_others_data(s3_client: boto3.client, s3_bucket: str) -> bool:
    """Xử lý dữ liệu others từ Bronze sang Silver - Based on actual structure."""
    debug_print("📊 Processing others data...")
    
    success_count = 0
    total_datasets = 0
    
    # Find all CSV files in bronze/others/raw/
    bronze_files = list_s3_files(s3_client, s3_bucket, f"{S3_BRONZE_OTHERS}/raw/")
    csv_files = [f for f in bronze_files if f.endswith('.csv')]
    
    debug_print(f"📊 Found {len(csv_files)} CSV files in others bronze layer")
    
    if not csv_files:
        debug_print("❌ No others data found in bronze layer", "ERROR")
        return False
    
    # Group files by type
    data_groups = {
        "macro": [],
        "vnindex": [],
        "financials": []
    }
    
    for csv_file in csv_files:
        filename = csv_file.split('/')[-1].lower()
        if any(x in filename for x in ['macro', 'gdp', 'cpi', 'interest', 'fx']):
            data_groups["macro"].append(csv_file)
        elif any(x in filename for x in ['vnindex', 'vn30']):
            data_groups["vnindex"].append(csv_file)
        elif 'financial' in filename or 'financial_reports' in csv_file:
            data_groups["financials"].append(csv_file)
        else:
            # Try to categorize by content or put in macro as default
            data_groups["macro"].append(csv_file)
    
    date_str = datetime.now().strftime("%Y%m%d")
    
    for data_type, files in data_groups.items():
        if not files:
            continue
            
        try:
            debug_print(f"🔄 Processing {data_type} data ({len(files)} files)...")
            
            # Read and combine files
            combined_data = []
            processed_files = []
            
            for file_path in files:
                df = read_csv_from_s3(s3_client, s3_bucket, file_path)
                if df is not None and not df.empty:
                    df['source_file'] = file_path.split('/')[-1]
                    combined_data.append(df)
                    processed_files.append(file_path)
                    total_datasets += 1
            
            if not combined_data:
                debug_print(f"⚠️ No valid data found for {data_type}")
                continue
            
            # Combine data
            df_combined = pd.concat(combined_data, ignore_index=True)
            debug_print(f"✅ Combined {len(df_combined)} records for {data_type}")
            
            # Clean data
            df_clean, transformation_log = clean_and_validate_data(df_combined, data_type)
            
            # Save processed data
            csv_content = df_clean.to_csv(index=False)
            csv_key = f"{S3_SILVER_BASE}/others/processed/clean_{data_type}_{date_str}.csv"
            csv_success = upload_to_s3(s3_client, s3_bucket, csv_content, csv_key, 'text/csv')
            
            # Create metadata
            metadata = {
                "dataset_info": {
                    "name": f"clean_{data_type}",
                    "description": f"Cleaned {data_type} data",
                    "rows": len(df_clean),
                    "columns": len(df_clean.columns),
                    "source_files": processed_files
                },
                "schema_info": {
                    "columns": list(df_clean.columns),
                    "data_types": {col: str(dtype) for col, dtype in df_clean.dtypes.items()}
                },
                "processing_info": {
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "transformation_log": transformation_log,
                    "processing_version": "4.0"
                }
            }
            
            # Upload metadata
            metadata_content = json.dumps(metadata, indent=2, ensure_ascii=False)
            metadata_key = f"{S3_SILVER_BASE}/others/metadata/{data_type}_metadata.json"
            metadata_success = upload_to_s3(s3_client, s3_bucket, metadata_content, metadata_key, 'application/json')
            
            if csv_success and metadata_success:
                success_count += 1
                debug_print(f"✅ {data_type} processing completed successfully")
            else:
                debug_print(f"⚠️ {data_type} processing partially successful")
                
        except Exception as e:
            debug_print(f"❌ Error processing {data_type}: {e}", "ERROR")
    
    debug_print(f"📊 Others processing: {success_count} datasets processed successfully")
    return success_count > 0

# ====== MAIN PROCESSING FUNCTION ======
def process_silver_data():
    """Main function để chuyển đổi dữ liệu từ Bronze sang Silver layer."""
    debug_print("🚀 Starting Bronze to Silver transformation")
    
    # Initialize S3
    s3_client = get_s3_client()
    s3_bucket = S3_BUCKET
    
    if not s3_client:
        debug_print("❌ Failed to initialize S3 client", "ERROR")
        return
    
    debug_print(f"✅ S3 initialized. Bucket: {s3_bucket}")
    
    # Process each data type
    results = {
        "stocks": False,
        "news": False,
        "others": False
    }
    
    # 1. Process stocks data
    try:
        results["stocks"] = process_stocks_data(s3_client, s3_bucket)
    except Exception as e:
        debug_print(f"❌ Error in stocks processing: {e}", "ERROR")
    
    # 2. Process news data
    try:
        results["news"] = process_news_data(s3_client, s3_bucket)
    except Exception as e:
        debug_print(f"❌ Error in news processing: {e}", "ERROR")
    
    # 3. Process others data
    try:
        results["others"] = process_others_data(s3_client, s3_bucket)
    except Exception as e:
        debug_print(f"❌ Error in others processing: {e}", "ERROR")
    
    # Final summary
    debug_print("\n" + "="*60)
    debug_print("🎉 SILVER LAYER PROCESSING COMPLETED!")
    debug_print("="*60)
    
    successful_processes = sum(results.values())
    total_processes = len(results)
    
    debug_print(f"📊 Processing Summary:")
    debug_print(f"   • Stocks: {'✅ Success' if results['stocks'] else '❌ Failed'}")
    debug_print(f"   • News: {'✅ Success' if results['news'] else '❌ Failed'}")
    debug_print(f"   • Others: {'✅ Success' if results['others'] else '❌ Failed'}")
    debug_print(f"   • Overall: {successful_processes}/{total_processes} successful")
    
    debug_print(f"\n📁 Silver Layer Structure:")
    debug_print(f"   s3://{s3_bucket}/{S3_SILVER_BASE}/")
    debug_print(f"   ├── stocks/")
    debug_print(f"   │   ├── processed/")
    debug_print(f"   │   │   ├── clean_stocks_{datetime.now().strftime('%Y%m%d')}.csv")
    debug_print(f"   │   │   └── clean_stocks_{datetime.now().strftime('%Y%m%d')}.parquet")
    debug_print(f"   │   └── metadata/")
    debug_print(f"   │       ├── stocks_metadata.json")
    debug_print(f"   │       └── transformation_log.json")
    debug_print(f"   ├── news/")
    debug_print(f"   │   ├── processed/")
    debug_print(f"   │   │   ├── clean_news_{datetime.now().strftime('%Y%m%d')}.csv")
    debug_print(f"   │   │   └── clean_news_{datetime.now().strftime('%Y%m%d')}.parquet")
    debug_print(f"   │   └── metadata/")
    debug_print(f"   │       ├── news_metadata.json")
    debug_print(f"   │       ├── schema_info.json")
    debug_print(f"   │       └── transformation_log.json")
    debug_print(f"   └── others/")
    debug_print(f"       ├── processed/")
    debug_print(f"       │   ├── clean_macro_{datetime.now().strftime('%Y%m%d')}.csv")
    debug_print(f"       │   ├── clean_vnindex_{datetime.now().strftime('%Y%m%d')}.csv")
    debug_print(f"       │   └── clean_financials_{datetime.now().strftime('%Y%m%d')}.csv")
    debug_print(f"       └── metadata/")
    debug_print(f"           ├── macro_metadata.json")
    debug_print(f"           ├── vnindex_metadata.json")
    debug_print(f"           └── financials_metadata.json")
    
    debug_print("="*60)

# ====== EXECUTION ======
if __name__ == "__main__":
    process_silver_data()