# ===============================================================
# 🏆 ETL: CHUYỂN DỮ LIỆU TỪ SILVER → GOLD (KAGGLE ENVIRONMENT)
# Version: v1.0 (Complete Gold Layer Implementation)
# ===============================================================

import boto3
import pandas as pd
import numpy as np
import io, json, os, time
from datetime import datetime, timezone, timedelta
import warnings
from typing import Dict, List, Optional, Tuple, Any
import re

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

# Import for sentiment analysis
try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("⚠️ TextBlob not available, using basic sentiment scoring")

# ====== KAGGLE ENVIRONMENT CONFIG ======
KAGGLE_WORKING_DIR = "/kaggle/working"
OUTPUT_GOLD_DIR = os.path.join(KAGGLE_WORKING_DIR, "gold_output")
OUTPUT_META_DIR = os.path.join(KAGGLE_WORKING_DIR, "gold_metadata")

# Create directories
os.makedirs(OUTPUT_GOLD_DIR, exist_ok=True)
os.makedirs(OUTPUT_META_DIR, exist_ok=True)

# S3 Configuration
S3_BUCKET = "bankanalystportfolio"
S3_SILVER_BASE = "silver"
S3_GOLD_BASE = "gold"

# Gold layer structure
GOLD_ANALYTICS = f"{S3_GOLD_BASE}/analytics"
GOLD_SERVING = f"{S3_GOLD_BASE}/serving"
GOLD_METADATA = f"{S3_GOLD_BASE}/metadata"
GOLD_LOGS = f"{S3_GOLD_BASE}/logs"

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

def read_parquet_from_s3(s3_client: boto3.client, bucket: str, key: str) -> Optional[pd.DataFrame]:
    """Đọc file Parquet từ S3."""
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        return pd.read_parquet(io.BytesIO(obj['Body'].read()))
    except Exception as e:
        debug_print(f"❌ Error reading parquet {key}: {e}", "ERROR")
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

def upload_to_s3(s3_client: boto3.client, bucket: str, content: Any, key: str, content_type: str = 'application/octet-stream') -> bool:
    """Upload content lên S3."""
    try:
        if isinstance(content, str):
            body = content.encode('utf-8')
        elif isinstance(content, bytes):
            body = content
        else:
            body = content
            
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

def get_latest_silver_file(s3_client: boto3.client, bucket: str, data_type: str) -> Optional[str]:
    """Tìm file Silver mới nhất cho data type."""
    try:
        silver_files = list_s3_files(s3_client, bucket, f"{S3_SILVER_BASE}/{data_type}/processed/")
        
        # Filter for CSV files and get the latest
        csv_files = [f for f in silver_files if f.endswith('.csv') and 'clean_' in f]
        if csv_files:
            # Sort by date in filename
            csv_files.sort(reverse=True)
            return csv_files[0]
        return None
    except Exception as e:
        debug_print(f"❌ Error finding latest silver file for {data_type}: {e}", "ERROR")
        return None

# ====== SENTIMENT ANALYSIS ======
def calculate_sentiment_score(text: str) -> float:
    """Tính sentiment score cho text."""
    try:
        if not text or pd.isna(text):
            return 0.0
        
        text = str(text).strip()
        if len(text) < 3:
            return 0.0
        
        if SENTIMENT_AVAILABLE:
            # Use TextBlob for sentiment analysis
            blob = TextBlob(text)
            return round(blob.sentiment.polarity, 4)
        else:
            # Basic sentiment using keyword matching
            positive_words = ['tăng', 'tích cực', 'khả quan', 'tốt', 'lợi nhuận', 'thành công', 'phát triển', 'cải thiện']
            negative_words = ['giảm', 'tiêu cực', 'xấu', 'lỗ', 'thất bại', 'khủng hoảng', 'rủi ro', 'suy giảm']
            
            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count + neg_count == 0:
                return 0.0
            
            return round((pos_count - neg_count) / (pos_count + neg_count), 4)
    except Exception as e:
        debug_print(f"⚠️ Error calculating sentiment: {e}", "WARNING")
        return 0.0

# ====== ADVANCED FEATURE ENGINEERING ======
def calculate_advanced_stock_features(df: pd.DataFrame) -> pd.DataFrame:
    """Tính toán các features nâng cao cho stocks."""
    try:
        df = df.copy()
        df = df.sort_values(['symbol', 'date']).reset_index(drop=True)
        
        def calculate_for_symbol(symbol_df):
            symbol_df = symbol_df.sort_values('date').reset_index(drop=True)
            
            # 1. Returns and Momentum
            symbol_df['daily_return'] = symbol_df['close'].pct_change()
            symbol_df['return_5d'] = symbol_df['close'].pct_change(periods=5)
            symbol_df['return_10d'] = symbol_df['close'].pct_change(periods=10)
            symbol_df['return_20d'] = symbol_df['close'].pct_change(periods=20)
            
            # 2. Momentum indicators
            symbol_df['momentum_5d'] = symbol_df['close'] / symbol_df['close'].shift(5) - 1
            symbol_df['momentum_10d'] = symbol_df['close'] / symbol_df['close'].shift(10) - 1
            
            # 3. Volatility measures
            symbol_df['volatility_5d'] = symbol_df['daily_return'].rolling(window=5).std()
            symbol_df['volatility_10d'] = symbol_df['daily_return'].rolling(window=10).std()
            symbol_df['volatility_20d'] = symbol_df['daily_return'].rolling(window=20).std()
            
            # 4. Price position relative to moving averages
            symbol_df['price_vs_ma5'] = symbol_df['close'] / symbol_df['MA_5'] - 1 if 'MA_5' in symbol_df.columns else 0
            symbol_df['price_vs_ma20'] = symbol_df['close'] / symbol_df['MA_20'] - 1 if 'MA_20' in symbol_df.columns else 0
            symbol_df['price_vs_ma50'] = symbol_df['close'] / symbol_df['MA_50'] - 1 if 'MA_50' in symbol_df.columns else 0
            
            # 5. Volume features
            symbol_df['volume_change'] = symbol_df['volume'].pct_change()
            symbol_df['volume_ma_ratio'] = symbol_df['volume'] / symbol_df['volume'].rolling(window=20).mean()
            
            # 6. Price range and body ratios
            symbol_df['price_range'] = (symbol_df['high'] - symbol_df['low']) / symbol_df['close']
            symbol_df['body_ratio'] = abs(symbol_df['close'] - symbol_df['open']) / (symbol_df['high'] - symbol_df['low'])
            
            # 7. Gap analysis
            symbol_df['gap'] = (symbol_df['open'] - symbol_df['close'].shift(1)) / symbol_df['close'].shift(1)
            
            # 8. Trend strength
            symbol_df['trend_strength_5d'] = np.where(
                symbol_df['close'] > symbol_df['close'].shift(5), 1, 
                np.where(symbol_df['close'] < symbol_df['close'].shift(5), -1, 0)
            )
            
            return symbol_df
        
        # Apply to each symbol
        if 'symbol' in df.columns:
            result_dfs = []
            for symbol in df['symbol'].unique():
                symbol_data = df[df['symbol'] == symbol].copy()
                symbol_processed = calculate_for_symbol(symbol_data)
                result_dfs.append(symbol_processed)
            final_df = pd.concat(result_dfs, ignore_index=True)
        else:
            final_df = calculate_for_symbol(df)
        
        debug_print(f"✅ Advanced stock features calculated")
        return final_df
        
    except Exception as e:
        debug_print(f"❌ Error calculating advanced features: {e}", "ERROR")
        return df

# ====== GOLD LAYER PROCESSING FUNCTIONS ======
def create_market_summary(s3_client: boto3.client, s3_bucket: str, stocks_df: pd.DataFrame, macro_df: pd.DataFrame) -> pd.DataFrame:
    """Tạo market summary table."""
    debug_print("📊 Creating market summary...")
    
    try:
        # Group by date for market-wide statistics
        market_summary = stocks_df.groupby('date').agg({
            'close': ['mean', 'median'],
            'volume': 'sum',
            'daily_return': 'mean',
            'volatility_20d': 'mean'
        }).reset_index()
        
        # Flatten column names
        market_summary.columns = ['date', 'avg_close', 'median_close', 'total_volume', 'avg_return', 'avg_volatility']
        
        # Add market trend
        market_summary['market_trend'] = np.where(market_summary['avg_return'] > 0, 'UP', 
                                                 np.where(market_summary['avg_return'] < 0, 'DOWN', 'FLAT'))
        
        # Merge with macro data if available
        if not macro_df.empty and 'date' in macro_df.columns:
            macro_df['date'] = pd.to_datetime(macro_df['date']).dt.date
            market_summary = pd.merge(market_summary, macro_df, on='date', how='left')
        
        # Add year/month for partitioning
        market_summary['year'] = pd.to_datetime(market_summary['date']).dt.year
        market_summary['month'] = pd.to_datetime(market_summary['date']).dt.month
        
        debug_print(f"✅ Market summary created with {len(market_summary)} records")
        return market_summary
        
    except Exception as e:
        debug_print(f"❌ Error creating market summary: {e}", "ERROR")
        return pd.DataFrame()

def create_stock_features_table(stocks_df: pd.DataFrame) -> pd.DataFrame:
    """Tạo bảng stock features cho ML."""
    debug_print("🔢 Creating stock features table...")
    
    try:
        # Select relevant features for ML
        feature_columns = [
            'symbol', 'date', 'open', 'high', 'low', 'close', 'volume',
            'daily_return', 'return_5d', 'return_10d', 'return_20d',
            'volatility_5d', 'volatility_10d', 'volatility_20d',
            'momentum_5d', 'momentum_10d'
        ]
        
        # Add technical indicators if available
        tech_indicators = ['MA_5', 'MA_10', 'MA_20', 'MA_50', 'RSI', 'MACD', 'BB_position']
        for indicator in tech_indicators:
            if indicator in stocks_df.columns:
                feature_columns.append(indicator)
        
        # Add advanced features if available
        advanced_features = ['price_vs_ma5', 'price_vs_ma20', 'volume_ma_ratio', 'trend_strength_5d']
        for feature in advanced_features:
            if feature in stocks_df.columns:
                feature_columns.append(feature)
        
        # Select only existing columns
        existing_columns = [col for col in feature_columns if col in stocks_df.columns]
        stock_features = stocks_df[existing_columns].copy()
        
        # Fill NaN values
        numeric_columns = stock_features.select_dtypes(include=[np.number]).columns
        stock_features[numeric_columns] = stock_features[numeric_columns].fillna(0)
        
        debug_print(f"✅ Stock features table created with {len(stock_features)} records and {len(existing_columns)} features")
        return stock_features
        
    except Exception as e:
        debug_print(f"❌ Error creating stock features: {e}", "ERROR")
        return pd.DataFrame()

def create_news_sentiment_table(news_df: pd.DataFrame) -> pd.DataFrame:
    """Tạo bảng sentiment analysis từ news."""
    debug_print("📰 Creating news sentiment table...")
    
    try:
        if news_df.empty:
            return pd.DataFrame()
        
        # Calculate sentiment if not already present
        if 'sentiment_score' not in news_df.columns:
            text_column = 'combined_text' if 'combined_text' in news_df.columns else 'title'
            if text_column in news_df.columns:
                debug_print(f"   Calculating sentiment scores for {len(news_df)} news articles...")
                news_df['sentiment_score'] = news_df[text_column].apply(calculate_sentiment_score)
        
        # Extract ticker from query or create general market sentiment
        if 'query' in news_df.columns:
            news_df['ticker'] = news_df['query'].str.upper()
        else:
            news_df['ticker'] = 'MARKET'  # General market sentiment
        
        # Group by ticker and date for aggregated sentiment
        sentiment_agg = news_df.groupby(['ticker', 'date']).agg({
            'sentiment_score': ['mean', 'std', 'count'],
            'id': 'count' if 'id' in news_df.columns else lambda x: len(x)
        }).reset_index()
        
        # Flatten column names
        sentiment_agg.columns = ['ticker', 'date', 'avg_sentiment', 'sentiment_volatility', 'sentiment_count', 'news_count']
        
        # Add sentiment categories
        sentiment_agg['sentiment_category'] = pd.cut(
            sentiment_agg['avg_sentiment'], 
            bins=[-1, -0.1, 0.1, 1], 
            labels=['NEGATIVE', 'NEUTRAL', 'POSITIVE']
        )
        
        debug_print(f"✅ News sentiment table created with {len(sentiment_agg)} records")
        return sentiment_agg
        
    except Exception as e:
        debug_print(f"❌ Error creating news sentiment: {e}", "ERROR")
        return pd.DataFrame()

def create_merged_stock_news_table(stocks_df: pd.DataFrame, sentiment_df: pd.DataFrame) -> pd.DataFrame:
    """Merge stocks data với sentiment data."""
    debug_print("🔗 Creating merged stock-news table...")
    
    try:
        if stocks_df.empty or sentiment_df.empty:
            debug_print("⚠️ Empty input data for merge", "WARNING")
            return stocks_df.copy() if not stocks_df.empty else pd.DataFrame()
        
        # Ensure date columns are in the same format
        stocks_df['date'] = pd.to_datetime(stocks_df['date']).dt.date
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date']).dt.date
        
        # Merge stocks with sentiment
        merged = pd.merge(
            stocks_df, 
            sentiment_df[['ticker', 'date', 'avg_sentiment', 'sentiment_volatility', 'news_count']], 
            left_on=['symbol', 'date'], 
            right_on=['ticker', 'date'], 
            how='left'
        )
        
        # Drop duplicate ticker column
        if 'ticker' in merged.columns:
            merged = merged.drop('ticker', axis=1)
        
        # Fill missing sentiment values
        merged['avg_sentiment'] = merged['avg_sentiment'].fillna(0)
        merged['sentiment_volatility'] = merged['sentiment_volatility'].fillna(0)
        merged['news_count'] = merged['news_count'].fillna(0)
        
        # Add interaction features
        merged['sentiment_return_interaction'] = merged['avg_sentiment'] * merged['daily_return']
        merged['sentiment_volume_interaction'] = merged['avg_sentiment'] * merged['volume_ma_ratio'] if 'volume_ma_ratio' in merged.columns else 0
        
        debug_print(f"✅ Merged table created with {len(merged)} records")
        return merged
        
    except Exception as e:
        debug_print(f"❌ Error creating merged table: {e}", "ERROR")
        return stocks_df.copy()

def create_ml_ready_dataset(merged_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Tạo dataset ready cho ML training."""
    debug_print("🤖 Creating ML-ready dataset...")
    
    try:
        if merged_df.empty:
            return pd.DataFrame(), pd.DataFrame()
        
        # Feature selection for ML
        feature_columns = []
        
        # Basic OHLCV features
        basic_features = ['open', 'high', 'low', 'close', 'volume']
        feature_columns.extend([col for col in basic_features if col in merged_df.columns])
        
        # Technical indicators
        tech_features = ['MA_5', 'MA_10', 'MA_20', 'RSI', 'MACD', 'BB_position', 'volatility_20d']
        feature_columns.extend([col for col in tech_features if col in merged_df.columns])
        
        # Advanced features
        advanced_features = ['daily_return', 'momentum_5d', 'volume_ma_ratio', 'avg_sentiment', 'news_count']
        feature_columns.extend([col for col in advanced_features if col in merged_df.columns])
        
        # Interaction features
        interaction_features = ['sentiment_return_interaction', 'sentiment_volume_interaction']
        feature_columns.extend([col for col in interaction_features if col in merged_df.columns])
        
        # Create features DataFrame
        X_features = merged_df[['symbol', 'date'] + feature_columns].copy()
        
        # Create labels (next day return as target)
        merged_sorted = merged_df.sort_values(['symbol', 'date'])
        merged_sorted['next_day_return'] = merged_sorted.groupby('symbol')['daily_return'].shift(-1)
        
        # Binary classification: positive vs negative return
        merged_sorted['target_direction'] = (merged_sorted['next_day_return'] > 0).astype(int)
        
        # Regression target: actual next day return
        y_labels = merged_sorted[['symbol', 'date', 'next_day_return', 'target_direction']].copy()
        
        # Remove rows with NaN targets
        valid_indices = ~y_labels['next_day_return'].isna()
        X_features = X_features[valid_indices].reset_index(drop=True)
        y_labels = y_labels[valid_indices].reset_index(drop=True)
        
        # Fill remaining NaN values in features
        numeric_columns = X_features.select_dtypes(include=[np.number]).columns
        X_features[numeric_columns] = X_features[numeric_columns].fillna(0)
        
        debug_print(f"✅ ML dataset created: {len(X_features)} samples, {len(feature_columns)} features")
        return X_features, y_labels
        
    except Exception as e:
        debug_print(f"❌ Error creating ML dataset: {e}", "ERROR")
        return pd.DataFrame(), pd.DataFrame()

def save_gold_table(s3_client: boto3.client, s3_bucket: str, df: pd.DataFrame, table_name: str, subfolder: str = "analytics") -> Dict:
    """Lưu bảng Gold và metadata."""
    try:
        if df.empty:
            debug_print(f"⚠️ Empty dataframe for {table_name}", "WARNING")
            return {"success": False, "error": "Empty dataframe"}
        
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Determine file paths
        if subfolder == "serving":
            folder_path = f"{GOLD_SERVING}/{table_name}"
        else:
            folder_path = f"{GOLD_ANALYTICS}/{table_name}"
        
        # Save as Parquet (preferred for analytics)
        parquet_key = f"{folder_path}/{table_name}_{date_str}.parquet"
        
        try:
            parquet_buffer = io.BytesIO()
            df.to_parquet(parquet_buffer, index=False, engine='pyarrow')
            parquet_success = upload_to_s3(s3_client, s3_bucket, parquet_buffer.getvalue(), parquet_key, 'application/octet-stream')
        except ImportError:
            debug_print("⚠️ PyArrow not available, saving as CSV instead", "WARNING")
            csv_key = f"{folder_path}/{table_name}_{date_str}.csv"
            csv_content = df.to_csv(index=False)
            parquet_success = upload_to_s3(s3_client, s3_bucket, csv_content, csv_key, 'text/csv')
            parquet_key = csv_key
        
        # Create and save metadata
        metadata = {
            "table_name": table_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "file_path": parquet_key,
            "file_format": "parquet" if parquet_key.endswith('.parquet') else "csv",
            "processing_version": "1.0",
            "schema": {
                col: {
                    "type": str(df[col].dtype),
                    "null_count": int(df[col].isnull().sum()),
                    "unique_count": int(df[col].nunique())
                } for col in df.columns
            }
        }
        
        # Add date range if date column exists
        if 'date' in df.columns:
            metadata["date_range"] = {
                "start": str(df['date'].min()),
                "end": str(df['date'].max())
            }
        
        metadata_key = f"{folder_path}/metadata.json"
        metadata_content = json.dumps(metadata, indent=2, ensure_ascii=False)
        metadata_success = upload_to_s3(s3_client, s3_bucket, metadata_content, metadata_key, 'application/json')
        
        return {
            "success": parquet_success and metadata_success,
            "data_path": parquet_key,
            "metadata_path": metadata_key,
            "rows": len(df),
            "columns": len(df.columns)
        }
        
    except Exception as e:
        debug_print(f"❌ Error saving {table_name}: {e}", "ERROR")
        return {"success": False, "error": str(e)}

# ====== MAIN GOLD PROCESSING FUNCTION ======
def process_gold_layer():
    """Main function để tạo Gold layer từ Silver data."""
    debug_print("🏆 Starting Silver to Gold transformation")
    
    # Initialize S3
    s3_client = get_s3_client()
    if not s3_client:
        debug_print("❌ Failed to initialize S3 client", "ERROR")
        return
    
    s3_bucket = S3_BUCKET
    debug_print(f"✅ S3 initialized. Bucket: {s3_bucket}")
    
    # Track processing results
    results = {}
    processing_log = {
        "start_time": datetime.now(timezone.utc).isoformat(),
        "tables_created": [],
        "errors": [],
        "summary": {}
    }
    
    try:
        # ===== 1. READ SILVER DATA =====
        debug_print("📖 Reading data from Silver layer...")
        
        # Read stocks data
        stocks_file = get_latest_silver_file(s3_client, s3_bucket, "stocks")
        if stocks_file:
            stocks_df = read_csv_from_s3(s3_client, s3_bucket, stocks_file)
            if stocks_df is not None and not stocks_df.empty:
                debug_print(f"✅ Loaded {len(stocks_df)} stock records")
                # Convert date column
                stocks_df['date'] = pd.to_datetime(stocks_df['date']).dt.date
                # Calculate advanced features
                stocks_df = calculate_advanced_stock_features(stocks_df)
            else:
                stocks_df = pd.DataFrame()
                debug_print("⚠️ No stocks data available", "WARNING")
        else:
            stocks_df = pd.DataFrame()
            debug_print("⚠️ No stocks file found in Silver", "WARNING")
        
        # Read news data
        news_file = get_latest_silver_file(s3_client, s3_bucket, "news")
        if news_file:
            news_df = read_csv_from_s3(s3_client, s3_bucket, news_file)
            if news_df is not None and not news_df.empty:
                debug_print(f"✅ Loaded {len(news_df)} news records")
                # Convert date column
                news_df['date'] = pd.to_datetime(news_df['date']).dt.date
            else:
                news_df = pd.DataFrame()
                debug_print("⚠️ No news data available", "WARNING")
        else:
            news_df = pd.DataFrame()
            debug_print("⚠️ No news file found in Silver", "WARNING")
        
        # Read macro/others data
        macro_file = get_latest_silver_file(s3_client, s3_bucket, "others")
        if not macro_file:
            # Try alternative paths
            silver_files = list_s3_files(s3_client, s3_bucket, f"{S3_SILVER_BASE}/others/processed/")
            macro_files = [f for f in silver_files if 'macro' in f or 'vnindex' in f]
            macro_file = macro_files[0] if macro_files else None
        
        if macro_file:
            macro_df = read_csv_from_s3(s3_client, s3_bucket, macro_file)
            if macro_df is not None and not macro_df.empty:
                debug_print(f"✅ Loaded {len(macro_df)} macro records")
                # Convert date column if exists
                if 'date' in macro_df.columns:
                    macro_df['date'] = pd.to_datetime(macro_df['date']).dt.date
            else:
                macro_df = pd.DataFrame()
        else:
            macro_df = pd.DataFrame()
            debug_print("⚠️ No macro data found", "WARNING")
        
        # ===== 2. CREATE GOLD TABLES =====
        debug_print("\n🏗️ Creating Gold layer tables...")
        
        # 2.1 Market Summary
        if not stocks_df.empty:
            market_summary = create_market_summary(s3_client, s3_bucket, stocks_df, macro_df)
            if not market_summary.empty:
                result = save_gold_table(s3_client, s3_bucket, market_summary, "market_summary", "analytics")
                results["market_summary"] = result
                if result["success"]:
                    processing_log["tables_created"].append("market_summary")
        
        # 2.2 Stock Features
        if not stocks_df.empty:
            stock_features = create_stock_features_table(stocks_df)
            if not stock_features.empty:
                result = save_gold_table(s3_client, s3_bucket, stock_features, "stock_features", "analytics")
                results["stock_features"] = result
                if result["success"]:
                    processing_log["tables_created"].append("stock_features")
        
        # 2.3 News Sentiment
        if not news_df.empty:
            news_sentiment = create_news_sentiment_table(news_df)
            if not news_sentiment.empty:
                result = save_gold_table(s3_client, s3_bucket, news_sentiment, "sentiment_analysis", "analytics")
                results["sentiment_analysis"] = result
                if result["success"]:
                    processing_log["tables_created"].append("sentiment_analysis")
        
        # 2.4 Merged Stock-News
        if not stocks_df.empty and not news_df.empty:
            # First create sentiment table
            sentiment_df = create_news_sentiment_table(news_df)
            if not sentiment_df.empty:
                merged_data = create_merged_stock_news_table(stocks_df, sentiment_df)
                if not merged_data.empty:
                    result = save_gold_table(s3_client, s3_bucket, merged_data, "merged_stock_news", "analytics")
                    results["merged_stock_news"] = result
                    if result["success"]:
                        processing_log["tables_created"].append("merged_stock_news")
                    
                    # 2.5 ML Ready Dataset
                    X_features, y_labels = create_ml_ready_dataset(merged_data)
                    if not X_features.empty and not y_labels.empty:
                        # Save features
                        feature_result = save_gold_table(s3_client, s3_bucket, X_features, "ml_features", "serving")
                        results["ml_features"] = feature_result
                        
                        # Save labels
                        label_result = save_gold_table(s3_client, s3_bucket, y_labels, "ml_labels", "serving")
                        results["ml_labels"] = label_result
                        
                        if feature_result["success"] and label_result["success"]:
                            processing_log["tables_created"].extend(["ml_features", "ml_labels"])
        
        # ===== 3. CREATE SUMMARY METADATA =====
        processing_log["end_time"] = datetime.now(timezone.utc).isoformat()
        processing_log["duration_minutes"] = round(
            (datetime.now(timezone.utc) - datetime.fromisoformat(processing_log["start_time"].replace('Z', '+00:00'))).total_seconds() / 60, 2
        )
        
        processing_log["summary"] = {
            "total_tables_created": len(processing_log["tables_created"]),
            "successful_tables": processing_log["tables_created"],
            "tables_with_errors": [table for table, result in results.items() if not result.get("success", False)],
            "input_data_summary": {
                "stocks_rows": len(stocks_df),
                "news_rows": len(news_df),
                "macro_rows": len(macro_df)
            },
            "output_data_summary": {
                table: {"rows": result.get("rows", 0), "columns": result.get("columns", 0)} 
                for table, result in results.items() if result.get("success", False)
            }
        }
        
        # Save processing log
        log_content = json.dumps(processing_log, indent=2, ensure_ascii=False)
        log_key = f"{GOLD_LOGS}/etl_gold_transform_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        upload_to_s3(s3_client, s3_bucket, log_content, log_key, 'application/json')
        
        # Create data catalog
        data_catalog = {
            "gold_layer_catalog": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "tables": {
                    table: {
                        "path": result.get("data_path"),
                        "metadata_path": result.get("metadata_path"),
                        "rows": result.get("rows", 0),
                        "columns": result.get("columns", 0),
                        "status": "success" if result.get("success") else "failed"
                    }
                    for table, result in results.items()
                },
                "analytics_tables": [t for t in processing_log["tables_created"] if t in ["market_summary", "stock_features", "sentiment_analysis", "merged_stock_news"]],
                "serving_tables": [t for t in processing_log["tables_created"] if t in ["ml_features", "ml_labels"]]
            }
        }
        
        catalog_content = json.dumps(data_catalog, indent=2, ensure_ascii=False)
        catalog_key = f"{GOLD_METADATA}/data_catalog.json"
        upload_to_s3(s3_client, s3_bucket, catalog_content, catalog_key, 'application/json')
        
        # ===== 4. FINAL SUMMARY =====
        debug_print("\n" + "="*60)
        debug_print("🏆 GOLD LAYER PROCESSING COMPLETED!")
        debug_print("="*60)
        
        successful_tables = len(processing_log["tables_created"])
        total_attempted = len(results)
        
        debug_print(f"📊 Processing Summary:")
        debug_print(f"   • Tables created: {successful_tables}/{total_attempted}")
        debug_print(f"   • Processing time: {processing_log['duration_minutes']} minutes")
        debug_print(f"   • Input records: Stocks({len(stocks_df)}), News({len(news_df)}), Macro({len(macro_df)})")
        
        debug_print(f"\n✅ Successfully created tables:")
        for table in processing_log["tables_created"]:
            result = results.get(table, {})
            debug_print(f"   • {table}: {result.get('rows', 0)} rows, {result.get('columns', 0)} columns")
        
        if len(processing_log["tables_created"]) < total_attempted:
            debug_print(f"\n❌ Failed tables:")
            for table, result in results.items():
                if not result.get("success", False):
                    debug_print(f"   • {table}: {result.get('error', 'Unknown error')}")
        
        debug_print(f"\n📁 Gold Layer Structure:")
        debug_print(f"   s3://{s3_bucket}/{S3_GOLD_BASE}/")
        debug_print(f"   ├── analytics/")
        debug_print(f"   │   ├── market_summary/")
        debug_print(f"   │   ├── stock_features/")
        debug_print(f"   │   ├── sentiment_analysis/")
        debug_print(f"   │   └── merged_stock_news/")
        debug_print(f"   ├── serving/")
        debug_print(f"   │   ├── ml_features/")
        debug_print(f"   │   └── ml_labels/")
        debug_print(f"   ├── metadata/")
        debug_print(f"   │   └── data_catalog.json")
        debug_print(f"   └── logs/")
        debug_print(f"       └── etl_gold_transform_log_*.json")
        
        debug_print("\n🎯 Ready for:")
        debug_print("   • Business Intelligence with Athena/QuickSight")
        debug_print("   • Machine Learning with feature store")
        debug_print("   • RAG pipeline with processed sentiment data")
        debug_print("   • Real-time dashboards and alerts")
        
        debug_print("="*60)
        
    except Exception as e:
        debug_print(f"❌ Critical error in Gold processing: {e}", "ERROR")
        processing_log["errors"].append(str(e))

# ====== EXECUTION ======
if __name__ == "__main__":
    process_gold_layer()