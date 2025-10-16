# ==============================================================================
# 📦 KAGGLE NEWS PROCESSING SCRIPT – CSV TO INDIVIDUAL JSON FILES
# Version: v2.0 (Optimized for Kaggle Environment)
# 
# Features:
# - Auto-detect CSV files in input directory
# - Robust error handling and logging
# - Memory-efficient processing with batch support
# - Data quality validation
# - Progress tracking
# - Metadata generation with statistics
# ==============================================================================

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import glob
import hashlib
import time
import boto3
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Import for Kaggle secrets
from kaggle_secrets import UserSecretsClient
try:
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    # Fallback for environments where botocore is not available
    class ClientError(Exception):
        pass
    class NoCredentialsError(Exception):
        pass

# ====== KAGGLE ENVIRONMENT CONFIG ======
KAGGLE_INPUT_DIR = "/kaggle/input"
KAGGLE_WORKING_DIR = "/kaggle/working"

# --- Đường dẫn file ---
INPUT_PATH = "/kaggle/input/vnindex-sentiment-v1/final_search_engine.csv"
OUTPUT_DIR = "/kaggle/working/processed"
OUTPUT_FILE = f"{OUTPUT_DIR}/financial_news_cleaned_{time.strftime('%Y%m%d')}.csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Auto-detect CSV files in input directory (fallback method)
def find_csv_files() -> List[str]:
    """Tự động tìm file CSV trong thư mục input của Kaggle."""
    csv_files = []
    for root, dirs, files in os.walk(KAGGLE_INPUT_DIR):
        for file in files:
            if file.lower().endswith('.csv'):
                full_path = os.path.join(root, file)
                csv_files.append(full_path)
    return csv_files

# Configuration with specific input path
if os.path.exists(INPUT_PATH):
    LOCAL_CSV_PATH = INPUT_PATH
    print(f"🎯 Using specified CSV file: {LOCAL_CSV_PATH}")
else:
    # Fallback to auto-detection
    csv_files = find_csv_files()
    if csv_files:
        LOCAL_CSV_PATH = csv_files[0]  # Sử dụng file CSV đầu tiên được tìm thấy
        print(f"🔍 Auto-detected CSV file: {LOCAL_CSV_PATH}")
    else:
        # Final fallback
        LOCAL_CSV_PATH = "/kaggle/input/news-data/news.csv"
        print(f"⚠️ Using fallback path: {LOCAL_CSV_PATH}")

OUTPUT_RAW_DIR = os.path.join(KAGGLE_WORKING_DIR, "news_json")
OUTPUT_META_DIR = os.path.join(KAGGLE_WORKING_DIR, "news_metadata")
BATCH_SIZE = 500  # Giảm batch size để tăng tốc
UPLOAD_BATCH_SIZE = 10  # Upload theo nhóm để tăng tốc

S3_BUCKET = "bankanalystportfolio"
S3_BASE_PATH_RAW = "bronze/news/raw"  # Bỏ s3:// prefix để đơn giản hóa
S3_BASE_PATH_META = "bronze/news/metadata"

# ====== S3 AND AWS CONFIGURATION ======
def get_s3_client() -> Optional[boto3.client]:
    """Khởi tạo S3 client với AWS credentials từ Kaggle secrets."""
    try:
        user_secrets = UserSecretsClient()
        aws_key_id = user_secrets.get_secret("AWS_ACCESS_KEY_ID")
        aws_secret = user_secrets.get_secret("AWS_SECRET_ACCESS_KEY")
        aws_region = user_secrets.get_secret("AWS_REGION")
        
        if not all([aws_key_id, aws_secret, aws_region]):
            debug_print("❌ LỖI: Không lấy được đầy đủ AWS credentials.", "ERROR")
            return None
            
        # Thêm cấu hình để tránh timeout
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
        try:
            client.list_buckets()
            debug_print("✅ S3 client khởi tạo thành công và có thể kết nối.")
        except ClientError as e:
            if e.response['Error']['Code'] == '403':
                debug_print("❌ LỖI 403: Không có quyền truy cập S3. Kiểm tra AWS credentials và permissions.", "ERROR")
            else:
                debug_print(f"❌ LỖI S3: {e}", "ERROR")
            return None
            
        return client
        
    except Exception as e:
        debug_print(f"❌ LỖI NGHIÊM TRỌNG khi khởi tạo S3 client: {e}", "ERROR")
        return None

def get_s3_bucket_name() -> Optional[str]:
    """Lấy tên S3 bucket từ Kaggle secrets."""
    try:
        bucket_name = UserSecretsClient().get_secret("S3_BUCKET")
        if not bucket_name:
            debug_print("❌ LỖI: Secret 'S3_BUCKET' trống hoặc không tồn tại.", "ERROR")
            return None
        debug_print(f"✅ Tìm thấy S3 bucket: {bucket_name}")
        return bucket_name
    except Exception as e:
        debug_print(f"❌ LỖI: Không tìm thấy secret 'S3_BUCKET': {e}", "ERROR")
        return None

def upload_file_to_s3(s3_client: boto3.client, s3_bucket: str, content: str, s3_key: str, content_type: str = 'application/json', metadata: Optional[Dict] = None) -> bool:
    """Upload content lên S3 với retry mechanism - tối ưu hóa."""
    max_retries = 2  # Giảm số lần retry
    
    for attempt in range(max_retries):
        try:
            s3_client.put_object(
                Bucket=s3_bucket,
                Key=s3_key,
                Body=content,
                ContentType=content_type,
                Metadata=metadata or {}
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '403':
                return False  # Không retry với lỗi 403
            elif error_code == 'NoSuchBucket':
                return False  # Không retry với lỗi bucket
            elif attempt < max_retries - 1:
                time.sleep(1)  # Giảm thời gian sleep
                    
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                return False
    
    return False

def batch_upload_to_s3(s3_client: boto3.client, s3_bucket: str, upload_items: List[Dict]) -> int:
    """Upload nhiều files cùng lúc để tăng tốc."""
    successful_uploads = 0
    
    for item in upload_items:
        success = upload_file_to_s3(
            s3_client, s3_bucket, 
            item['content'], item['key'], 
            item['content_type'], item.get('metadata')
        )
        if success:
            successful_uploads += 1
    
    return successful_uploads

# ====== UTILITY FUNCTIONS ======
def debug_print(message: str, level: str = "INFO"):
    """Enhanced logging with timestamps and levels."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}", flush=True)

def create_padded_id(index: int, total_count: int) -> str:
    """Tạo ID có padding dựa trên index và tổng số record."""
    # Tính số chữ số cần thiết dựa trên tổng số record
    if total_count < 1000:
        padding = 3  # 000-999
    elif total_count < 10000:
        padding = 4  # 0000-9999
    elif total_count < 100000:
        padding = 5  # 00000-99999
    else:
        padding = 6  # 000000-999999
    
    return f"{index:0{padding}d}"

def create_safe_filename(text: str, max_length: int = 50) -> str:
    """Tạo tên file an toàn từ text."""
    import re
    # Remove special characters and limit length
    safe_text = re.sub(r'[^\w\s-]', '', str(text))
    safe_text = re.sub(r'[-\s]+', '-', safe_text)
    return safe_text[:max_length].strip('-')

def calculate_file_hash(content: str) -> str:
    """Tính hash của nội dung để detect duplicates."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]

def validate_news_data(row: pd.Series) -> Tuple[bool, List[str]]:
    """Validate dữ liệu tin tức và trả về status + lỗi."""
    errors = []
    
    # Kiểm tra các trường bắt buộc
    required_fields = ['id']
    for field in required_fields:
        if pd.isna(row.get(field)) or str(row.get(field)).strip() == '':
            errors.append(f"Missing required field: {field}")
    
    # Kiểm tra content có ý nghĩa
    title = str(row.get('title', ''))
    content = str(row.get('combined_text', ''))
    
    if len(title.strip()) < 3 and len(content.strip()) < 10:
        errors.append("Title and content too short")
    
    # Kiểm tra date format
    try:
        if not pd.isna(row.get('date')):
            pd.to_datetime(row.get('date'))
    except:
        errors.append("Invalid date format")
    
    return len(errors) == 0, errors

def process_batch(df_batch: pd.DataFrame, batch_num: int, start_index: int, total_count: int, s3_client: boto3.client, s3_bucket: str) -> Dict:
    """Xử lý một batch dữ liệu với sequential ID numbering và upload theo nhóm lên S3."""
    debug_print(f"🔄 Batch {batch_num}: Processing {len(df_batch)} records...")
    
    stats = {
        'processed': 0,
        'successful': 0,
        'skipped': 0,
        'errors': 0,
        'error_details': []
    }
    
    upload_items = []  # Tập hợp để upload theo batch
    
    for batch_idx, (df_idx, row) in enumerate(df_batch.iterrows()):
        stats['processed'] += 1
        
        try:
            # Quick validation - chỉ kiểm tra essential
            original_id = row.get('id')
            if pd.isna(original_id) or str(original_id).strip() == '':
                stats['skipped'] += 1
                continue
            
            # Use original ID as filename (clean it for safety)
            file_id = str(original_id).strip()
            # Remove any characters that might be problematic for filenames
            import re
            file_id = re.sub(r'[^\w\-.]', '_', file_id)
            
            # Generate sequential padded ID for internal tracking only
            sequential_index = start_index + batch_idx + 1
            padded_id = create_padded_id(sequential_index, total_count)
            
            # Prepare news data - simplified
            news_data = {
                "id": file_id,  # Use original ID as primary ID
                "sequential_id": padded_id,  # Keep sequential for reference
                "query": str(row.get("query", "")) if not pd.isna(row.get("query")) else None,
                "source": str(row.get("source", "")) if not pd.isna(row.get("source")) else None,
                "link": str(row.get("link", "")) if not pd.isna(row.get("link")) else None,
                "title": str(row.get("title", "")) if not pd.isna(row.get("title")) else None,
                "combined_text": str(row.get("combined_text", "")) if not pd.isna(row.get("combined_text")) else None,
                "date": str(row.get("date")) if not pd.isna(row.get("date")) else None,
                "_ingest_time_utc": datetime.now(timezone.utc).isoformat(),
                "_schema_version": "1.0"
            }
            
            # Add to upload batch - use original ID as filename
            upload_items.append({
                'content': json.dumps(news_data, ensure_ascii=False),
                'key': f"{S3_BASE_PATH_RAW}/{file_id}.json",
                'content_type': 'application/json',
                'metadata': {
                    'id': file_id,
                    'data_type': 'news_article'
                }
            })
            
            # Simplified metadata
            title_length = len(str(row.get("title", ""))) if not pd.isna(row.get("title")) else 0
            content_length = len(str(row.get("combined_text", ""))) if not pd.isna(row.get("combined_text")) else 0
            
            meta_data = {
                "id": file_id,  # Use original ID
                "sequential_id": padded_id,  # Keep sequential for reference
                "source": str(row.get("source", "")) if not pd.isna(row.get("source")) else None,
                "title_length": title_length,
                "content_length": content_length,
                "_processing_info": {
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "batch_number": batch_num,
                    "sequential_index": sequential_index
                }
            }
            
            # Add metadata to upload batch - use original ID as filename
            upload_items.append({
                'content': json.dumps(meta_data, ensure_ascii=False),
                'key': f"{S3_BASE_PATH_META}/{file_id}_metadata.json",
                'content_type': 'application/json',
                'metadata': {
                    'id': file_id,
                    'metadata_type': 'news_metadata'
                }
            })
            
            # Upload in groups to improve speed
            if len(upload_items) >= UPLOAD_BATCH_SIZE * 2:  # *2 vì có cả news và metadata
                successful_uploads = batch_upload_to_s3(s3_client, s3_bucket, upload_items)
                stats['successful'] += successful_uploads // 2  # Chia 2 vì mỗi news có 2 files
                upload_items.clear()
            
        except Exception as e:
            stats['errors'] += 1
            continue
    
    # Upload remaining items
    if upload_items:
        successful_uploads = batch_upload_to_s3(s3_client, s3_bucket, upload_items)
        stats['successful'] += successful_uploads // 2
    
    debug_print(f"✅ Batch {batch_num}: {stats['successful']}/{stats['processed']} successful")
    return stats

# ====== MAIN PROCESSING FUNCTION ======
def process_news_csv():
    """Main function để xử lý CSV thành JSON files và upload lên S3."""
    debug_print("🚀 Starting news CSV to JSON processing with S3 upload")
    
    # Initialize S3 client and bucket
    debug_print("🔄 Initializing S3 connection...")
    s3_client = get_s3_client()
    s3_bucket = get_s3_bucket_name()
    
    if not s3_client or not s3_bucket:
        debug_print("❌ DỪNG: Không thể khởi tạo S3 client hoặc lấy bucket name.", "ERROR")
        return
    
    debug_print(f"✅ S3 connection established. Bucket: {s3_bucket}")
    
    # Create local output directories for temporary processing (optional)
    os.makedirs(OUTPUT_RAW_DIR, exist_ok=True)
    os.makedirs(OUTPUT_META_DIR, exist_ok=True)
    debug_print(f"📁 Local directories created: {OUTPUT_RAW_DIR}, {OUTPUT_META_DIR}")
    
    # Check if CSV file exists
    if not os.path.exists(LOCAL_CSV_PATH):
        debug_print(f"❌ CSV file not found: {LOCAL_CSV_PATH}", "ERROR")
        debug_print("📋 Available files in input directory:")
        for root, dirs, files in os.walk(KAGGLE_INPUT_DIR):
            for file in files:
                debug_print(f"   📄 {os.path.join(root, file)}")
        return
    
    # Read CSV with error handling
    try:
        debug_print(f"📖 Reading CSV file: {LOCAL_CSV_PATH}")
        df = pd.read_csv(LOCAL_CSV_PATH)
        debug_print(f"✅ Loaded {len(df)} news articles")
        debug_print(f"📊 Columns: {list(df.columns)}")
        
        # Display basic statistics
        debug_print(f"📈 Data overview:")
        debug_print(f"   • Total rows: {len(df)}")
        debug_print(f"   • Total columns: {len(df.columns)}")
        debug_print(f"   • Missing values per column:")
        for col in df.columns:
            missing = df[col].isna().sum()
            debug_print(f"     - {col}: {missing} ({missing/len(df)*100:.1f}%)")
            
    except Exception as e:
        debug_print(f"❌ Error reading CSV: {e}", "ERROR")
        return
    
    # Data preprocessing
    debug_print("🔄 Preprocessing data...")
    original_count = len(df)
    
    # Remove rows without essential data
    essential_columns = ['id']
    for col in essential_columns:
        if col in df.columns:
            df = df.dropna(subset=[col])
    
    # Remove duplicates based on ID
    df = df.drop_duplicates(subset=['id'], keep='first')
    
    # Convert date column if exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    debug_print(f"📊 After preprocessing: {len(df)} articles (removed {original_count - len(df)})")
    
    # Process in batches with sequential numbering and S3 upload
    total_stats = {
        'total_batches': 0,
        'total_processed': 0,
        'total_successful': 0,
        'total_skipped': 0,
        'total_errors': 0,
        'all_error_details': []
    }
    
    # Calculate number of batches
    num_batches = (len(df) - 1) // BATCH_SIZE + 1
    debug_print(f"🔢 Processing {len(df)} articles in {num_batches} batches (batch size: {BATCH_SIZE})")
    
    # Track successful records count for sequential numbering
    successful_count = 0
    
    for batch_num in range(num_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min((batch_num + 1) * BATCH_SIZE, len(df))
        
        df_batch = df.iloc[start_idx:end_idx]
        batch_stats = process_batch(df_batch, batch_num + 1, successful_count, len(df), s3_client, s3_bucket)
        
        # Update successful count for next batch
        successful_count += batch_stats['successful']
        
        # Aggregate stats
        total_stats['total_batches'] += 1
        total_stats['total_processed'] += batch_stats['processed']
        total_stats['total_successful'] += batch_stats['successful']
        total_stats['total_skipped'] += batch_stats['skipped']
        total_stats['total_errors'] += batch_stats['errors']
        total_stats['all_error_details'].extend(batch_stats['error_details'])
        
        # Progress update
        progress = ((batch_num + 1) / num_batches) * 100
        debug_print(f"📊 Progress: {progress:.1f}% - Batch {batch_num + 1}/{num_batches} completed")
    
    # Upload original CSV to S3
    debug_print("📄 Uploading original CSV to S3...")
    try:
        with open(LOCAL_CSV_PATH, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        csv_upload_success = upload_file_to_s3(
            s3_client, s3_bucket, csv_content, f"{S3_BASE_PATH_RAW}/news_data.csv",
            content_type='text/csv',
            metadata={
                'data_type': 'original_news_csv',
                'total_records': str(len(df))
            }
        )
        
        if csv_upload_success:
            debug_print(f"✅ Original CSV uploaded to S3")
        else:
            debug_print("⚠️ Failed to upload CSV", "WARNING")
            
    except Exception as e:
        debug_print(f"⚠️ Could not upload CSV: {e}", "WARNING")
    
    # Final summary
    debug_print("\n" + "="*60)
    debug_print("📋 PROCESSING SUMMARY")
    debug_print("="*60)
    debug_print(f"✅ Total articles processed: {total_stats['total_processed']}")
    debug_print(f"✅ Successful conversions: {total_stats['total_successful']}")
    debug_print(f"⚠️ Skipped (validation failed): {total_stats['total_skipped']}")
    debug_print(f"❌ Errors: {total_stats['total_errors']}")
    
    if total_stats['total_processed'] > 0:
        success_rate = (total_stats['total_successful'] / total_stats['total_processed']) * 100
        debug_print(f"📊 Success rate: {success_rate:.2f}%")
    
    debug_print(f"📁 JSON files uploaded to S3: {total_stats['total_successful']}")
    debug_print(f"📁 Metadata files uploaded to S3: {total_stats['total_successful']}")
    
    # Show some error examples if any
    if total_stats['all_error_details']:
        debug_print(f"\n⚠️ Error examples (showing first 5):")
        for i, error in enumerate(total_stats['all_error_details'][:5]):
            debug_print(f"   {i+1}. Original ID: {error['original_id']} - {error.get('errors', error.get('error'))}")
    
    # Create and upload news summary metadata
    debug_print("📄 Creating and uploading news summary metadata...")
    news_summary_metadata = {
        "processing_summary": total_stats,
        "dataset_info": {
            "total_records_in_source": original_count,
            "records_after_preprocessing": len(df),
            "successful_json_files": total_stats['total_successful'],
            "padding_format": create_padded_id(1, total_stats['total_successful']).replace('1', 'X') if total_stats['total_successful'] > 0 else "000XXX"
        },
        "file_structure": {
            "s3_bucket": s3_bucket,
            "s3_raw_path": f"s3://{s3_bucket}/{S3_BASE_PATH_RAW}",
            "s3_metadata_path": f"s3://{s3_bucket}/{S3_BASE_PATH_META}",
            "files_generated": {
                "individual_json_files": "Uses original IDs as filenames (e.g., ea32619b-c587-4ca1-9a30-2cfebb1b033a.json)",
                "metadata_files": "Uses original IDs as filenames (e.g., ea32619b-c587-4ca1-9a30-2cfebb1b033a_metadata.json)",
                "original_csv": "news_data.csv",
                "summary_metadata": "news_summary_metadata.json"
            }
        },
        "data_quality_summary": {
            "avg_title_length": 0,
            "avg_content_length": 0,
            "sources_distribution": {},
            "date_range": {"earliest": None, "latest": None}
        },
        "processing_info": {
            "source_csv": LOCAL_CSV_PATH,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "batch_size": BATCH_SIZE,
            "s3_upload": True,
            "schema_version": "1.0"
        }
    }
    
    # Calculate basic data quality summary from original dataframe
    if total_stats['total_successful'] > 0 and not df.empty:
        try:
            # Calculate from original dataframe since we uploaded directly to S3
            title_lengths = []
            content_lengths = []
            sources = []
            dates = []
            
            for _, row in df.head(100).iterrows():  # Sample first 100 rows for stats
                if not pd.isna(row.get('title')):
                    title_lengths.append(len(str(row.get('title', ''))))
                if not pd.isna(row.get('combined_text')):
                    content_lengths.append(len(str(row.get('combined_text', ''))))
                if not pd.isna(row.get('source')):
                    sources.append(str(row.get('source')))
                if not pd.isna(row.get('date')):
                    dates.append(str(row.get('date')))
            
            if title_lengths:
                news_summary_metadata["data_quality_summary"]["avg_title_length"] = round(sum(title_lengths) / len(title_lengths), 2)
            if content_lengths:
                news_summary_metadata["data_quality_summary"]["avg_content_length"] = round(sum(content_lengths) / len(content_lengths), 2)
            if sources:
                from collections import Counter
                news_summary_metadata["data_quality_summary"]["sources_distribution"] = dict(Counter(sources))
            if dates:
                news_summary_metadata["data_quality_summary"]["date_range"] = {
                    "earliest": min(dates),
                    "latest": max(dates)
                }
        except Exception as e:
            debug_print(f"⚠️ Could not calculate data quality summary: {e}", "WARNING")
    
    # Upload news summary metadata to S3
    summary_json_content = json.dumps(news_summary_metadata, ensure_ascii=False)
    
    summary_upload_success = upload_file_to_s3(
        s3_client, s3_bucket, summary_json_content, f"{S3_BASE_PATH_META}/news_summary_metadata.json",
        content_type='application/json',
        metadata={
            'metadata_type': 'ingestion_summary',
            'total_successful': str(total_stats['total_successful'])
        }
    )
    
    if summary_upload_success:
        debug_print(f"📄 Summary metadata uploaded to S3")
    
    debug_print("="*60)
    debug_print("🎉 S3 UPLOAD COMPLETED!")
    debug_print(f"✅ Total files uploaded: {total_stats['total_successful'] * 2 + 2}")  # news + metadata + csv + summary

# ====== EXECUTION ======
if __name__ == "__main__":
    process_news_csv()
