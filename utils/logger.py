import json
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET") or os.getenv("AWS_BUCKET_NAME")

# Initialize S3 client
s3_client = None
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_REGION:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

def log_execution_to_s3(log_data, log_type="general", prefix="logs/"):
    """
    Save execution metadata as JSON into S3.
    
    Args:
        log_data: Dict chứa thông tin execution
        log_type: Loại log ("ohlcv", "news", "general")
        prefix: Prefix cho S3 key
    """
    # Bổ sung timestamp nếu thiếu
    if "timestamp" not in log_data:
        log_data["timestamp"] = datetime.utcnow().isoformat()
    
    # Bổ sung log_type
    log_data["log_type"] = log_type
    
    # Tạo key (đường dẫn trong bucket)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    timestamp_str = int(datetime.utcnow().timestamp())
    
    if log_type == "ohlcv":
        symbol = log_data.get("symbol", "all_stocks")
        log_key = f"{prefix}ohlcv/date={date_str}/{symbol}_{timestamp_str}.json"
    elif log_type == "news":
        source = log_data.get("source", "all_sources")
        log_key = f"{prefix}news/date={date_str}/{source}_{timestamp_str}.json"
    else:
        log_key = f"{prefix}general/date={date_str}/execution_{timestamp_str}.json"

    try:
        if s3_client and S3_BUCKET:
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=log_key,
                Body=json.dumps(log_data, ensure_ascii=False, indent=2),
                ContentType="application/json"
            )
            print(f"📝 Log saved to s3://{S3_BUCKET}/{log_key}")
            return True
        else:
            # Fallback to local logging
            local_path = f"/tmp/{log_key}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            print(f"📝 Log saved locally: {local_path}")
            return True
            
    except Exception as e:
        print(f"❌ Failed to save log: {e}")
        return False

def create_ohlcv_log(symbol, target_date, status, details=None, error=None):
    """
    Tạo log data cho OHLCV crawling
    
    Args:
        symbol: Mã cổ phiếu hoặc "all_stocks"
        target_date: Ngày crawl
        status: "success", "failed", "partial"
        details: Dict chứa thông tin chi tiết (số stocks thành công, thất bại, etc.)
        error: Thông tin lỗi nếu có
    """
    log_data = {
        "script": "ingest_stock.py",
        "symbol": symbol,
        "target_date": target_date,
        "status": status,
        "execution_time": datetime.utcnow().isoformat()
    }
    
    if details:
        log_data["details"] = details
    
    if error:
        log_data["error"] = str(error)
    
    return log_data

def create_news_log(target_date, status, details=None, error=None):
    """
    Tạo log data cho News crawling
    
    Args:
        target_date: Ngày crawl
        status: "success", "failed", "partial"
        details: Dict chứa thông tin chi tiết (số articles, sources, etc.)
        error: Thông tin lỗi nếu có
    """
    log_data = {
        "script": "ingest_news.py",
        "target_date": target_date,
        "status": status,
        "execution_time": datetime.utcnow().isoformat()
    }
    
    if details:
        log_data["details"] = details
    
    if error:
        log_data["error"] = str(error)
    
    return log_data

def log_ohlcv_execution(symbol, target_date, status, **kwargs):
    """
    Wrapper function để log OHLCV execution
    """
    log_data = create_ohlcv_log(symbol, target_date, status, **kwargs)
    return log_execution_to_s3(log_data, log_type="ohlcv")

def log_news_execution(target_date, status, **kwargs):
    """
    Wrapper function để log News execution
    """
    log_data = create_news_log(target_date, status, **kwargs)
    return log_execution_to_s3(log_data, log_type="news")
