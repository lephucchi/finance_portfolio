# ==============================================================================
# Kaggle notebook: lakehose initial ingestion (Stocks with VNStock support)
#
# Version: v6.1 (Fixed 403 Forbidden & Rate Limiting Issues)
# Changes:
# - Fixed import error: botocore.exceptions instead of botore.exceptions
# - Added proper error handling for S3 operations
# - Improved rate limiting and request headers
# - Enhanced vnstock3 configuration for stability
# - Added retry mechanism with exponential backoff
# ==============================================================================

# pip install --upgrade vnstock3 boto3 --quiet

import json
import time
import sys
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import warnings
warnings.filterwarnings('ignore')

import boto3
import pandas as pd
from vnstock3 import Vnstock
from kaggle_secrets import UserSecretsClient
try:
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    # Fallback for environments where botocore is not available
    class ClientError(Exception):
        pass
    class NoCredentialsError(Exception):
        pass

# --- [CẬP NHẬT] Cấu hình S3 path structure mới ---
S3_BASE_PATH = 'bronze/stocks'
S3_RAW_PATH = f'{S3_BASE_PATH}/raw'
S3_METADATA_PATH = f'{S3_BASE_PATH}/metadata'
S3_INDEX_PATH = f'{S3_RAW_PATH}/index'

MAX_WORKERS = 2                 # Giảm thêm số luồng song song
REQUEST_DELAY_SECONDS = 2.5     # Tăng thời gian nghỉ để tránh rate limit
RETRY_DELAY_SECONDS = 5.0       # Thời gian nghỉ khi retry
MAX_RETRIES = 3                 # Số lần retry tối đa
START_DATE = '2020-01-01'       # Lấy dữ liệu từ 2020

# --- Hàm hỗ trợ ---
def debug_print(message: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - {message}", flush=True)

def exponential_backoff(attempt: int, base_delay: float = 1.0) -> float:
    """Tính toán thời gian chờ theo exponential backoff"""
    return base_delay * (2 ** attempt) + random.uniform(0, 1)

# ... (Các hàm get_s3_client, get_s3_bucket_name được cải thiện) ...
def get_s3_client() -> Optional[boto3.client]:
    try:
        user_secrets = UserSecretsClient()
        aws_key_id = user_secrets.get_secret("AWS_ACCESS_KEY_ID")
        aws_secret = user_secrets.get_secret("AWS_SECRET_ACCESS_KEY")
        aws_region = user_secrets.get_secret("AWS_REGION")
        
        if not all([aws_key_id, aws_secret, aws_region]):
            debug_print("❌ LỖI: Không lấy được đầy đủ AWS credentials.")
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
                debug_print("❌ LỖI 403: Không có quyền truy cập S3. Kiểm tra AWS credentials và permissions.")
            else:
                debug_print(f"❌ LỖI S3: {e}")
            return None
            
        return client
        
    except Exception as e:
        debug_print(f"❌ LỖI NGHIÊM TRỌNG khi khởi tạo S3 client: {e}")
        return None

def get_s3_bucket_name() -> Optional[str]:
    try:
        bucket_name = UserSecretsClient().get_secret("S3_BUCKET")
        if not bucket_name:
            debug_print("❌ LỖI: Secret 'S3_BUCKET' trống hoặc không tồn tại.")
            return None
        debug_print(f"✅ Tìm thấy S3 bucket: {bucket_name}")
        return bucket_name
    except Exception as e:
        debug_print(f"❌ LỖI: Không tìm thấy secret 'S3_BUCKET': {e}")
        return None

# --- [CẬP NHẬT] Hàm Fetch dữ liệu với xử lý lỗi tốt hơn ---
def fetch_vn_ohlcv(vnstock_instance: Vnstock, ticker: str) -> pd.DataFrame:
    """Lấy dữ liệu OHLCV với xử lý lỗi và retry cải thiện."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    for attempt in range(MAX_RETRIES):
        try:
            # Thêm delay để tránh rate limit
            if attempt > 0:
                delay = exponential_backoff(attempt, RETRY_DELAY_SECONDS)
                debug_print(f"-> {ticker}: Retry {attempt + 1}/{MAX_RETRIES} sau {delay:.1f}s...")
                time.sleep(delay)
            
            # Cấu hình stock instance với source khác nhau để tăng tính ổn định
            sources = ['TCBS', 'VCI', 'VND']
            source = sources[attempt % len(sources)]
            
            stock = vnstock_instance.stock(symbol=ticker, source=source)
            df = stock.quote.history(start=START_DATE, end=end_date, interval='1D')
            
            if df is None or df.empty: 
                debug_print(f"-> {ticker}: Không có dữ liệu từ source {source}")
                continue
            
            # Đảm bảo có đủ cột cần thiết
            required_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                debug_print(f"-> {ticker}: Thiếu cột dữ liệu cần thiết từ source {source}")
                continue
            
            # Xử lý dữ liệu
            df = df[required_columns].copy()
            df.rename(columns={
                'time': 'Date', 'open': 'Open', 'high': 'High', 
                'low': 'Low', 'close': 'Close', 'volume': 'Volume'
            }, inplace=True)
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
            
            # Loại bỏ các dòng có dữ liệu không hợp lệ
            df = df.dropna()
            
            debug_print(f"-> {ticker}: Lấy được {len(df)} ngày dữ liệu từ source {source}")
            return df
            
        except Exception as e:
            debug_print(f"-> {ticker}: Lỗi attempt {attempt + 1}: {e}")
            if attempt == MAX_RETRIES - 1:
                debug_print(f"-> {ticker}: Đã thử hết {MAX_RETRIES} lần, bỏ qua mã này.")
                return pd.DataFrame()
    
    return pd.DataFrame()

# --- [MỚI] Hàm tạo metadata cho cổ phiếu ---
def create_stock_metadata(ticker: str, df: pd.DataFrame, source: str, ingest_time: datetime) -> Dict:
    """Tạo metadata cho cổ phiếu."""
    if df.empty:
        return {}
    
    return {
        'ticker': ticker,
        'total_records': len(df),
        'date_range': {
            'start_date': df['Date'].min(),
            'end_date': df['Date'].max()
        },
        'data_quality': {
            'missing_values': df.isnull().sum().to_dict(),
            'data_completeness': f"{((len(df) - df.isnull().sum().sum()) / (len(df) * len(df.columns)) * 100):.2f}%"
        },
        'price_statistics': {
            'min_close': float(df['Close'].min()),
            'max_close': float(df['Close'].max()),
            'avg_close': float(df['Close'].mean()),
            'min_volume': int(df['Volume'].min()),
            'max_volume': int(df['Volume'].max()),
            'avg_volume': int(df['Volume'].mean())
        },
        '_source': source,
        '_ingest_time_utc': ingest_time.isoformat() + 'Z',
        '_schema_version': '1.0'
    }

def upload_stock_metadata(s3_client: boto3.client, s3_bucket: str, ticker: str, metadata: Dict) -> bool:
    """Upload metadata cho cổ phiếu lên S3."""
    try:
        metadata_key = f"{S3_METADATA_PATH}/{ticker}_metadata.json"
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=metadata_key,
            Body=json.dumps(metadata, ensure_ascii=False, indent=2),
            ContentType='application/json',
            Metadata={
                'ticker': ticker,
                'metadata_type': 'stock_metadata',
                'schema_version': '1.0'
            }
        )
        debug_print(f"✅ [METADATA] {ticker}: Đã upload metadata")
        return True
    except Exception as e:
        debug_print(f"❌ [METADATA ERROR] {ticker}: {e}")
        return False

# --- [MỚI] Hàm tạo summary metadata ---
def create_summary_metadata(successful_tickers: List[Dict], failed_tickers: List[str], 
                          total_files: int, processing_time: float, ingest_time: datetime) -> Dict:
    """Tạo summary metadata cho toàn bộ quá trình ingestion."""
    return {
        'ingestion_summary': {
            'total_tickers_processed': len(successful_tickers) + len(failed_tickers),
            'successful_tickers': len(successful_tickers),
            'failed_tickers': len(failed_tickers),
            'success_rate': f"{(len(successful_tickers) / (len(successful_tickers) + len(failed_tickers)) * 100):.2f}%",
            'total_files_uploaded': total_files,
            'processing_time_seconds': round(processing_time, 2)
        },
        'successful_tickers': [ticker['ticker'] for ticker in successful_tickers],
        'failed_tickers': failed_tickers,
        'detailed_results': successful_tickers,
        'data_structure': {
            'raw_data_path': S3_RAW_PATH,
            'metadata_path': S3_METADATA_PATH,
            'index_path': S3_INDEX_PATH
        },
        '_ingest_time_utc': ingest_time.isoformat() + 'Z',
        '_schema_version': '1.0'
    }

def upload_summary_metadata(s3_client: boto3.client, s3_bucket: str, summary_metadata: Dict) -> bool:
    """Upload summary metadata lên S3."""
    try:
        summary_key = f"{S3_METADATA_PATH}/stocks_summary_metadata.json"
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=summary_key,
            Body=json.dumps(summary_metadata, ensure_ascii=False, indent=2),
            ContentType='application/json',
            Metadata={
                'metadata_type': 'ingestion_summary',
                'schema_version': '1.0'
            }
        )
        debug_print(f"✅ [SUMMARY METADATA] Đã upload summary metadata")
        return True
    except Exception as e:
        debug_print(f"❌ [SUMMARY METADATA ERROR] {e}")
        return False

# --- [MỚI] Hàm xử lý chỉ số thị trường ---
def fetch_market_index(vnstock_instance: Vnstock, index_symbol: str) -> pd.DataFrame:
    """Lấy dữ liệu chỉ số thị trường (VNINDEX, VN30)."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    for attempt in range(MAX_RETRIES):
        try:
            if attempt > 0:
                delay = exponential_backoff(attempt, RETRY_DELAY_SECONDS)
                debug_print(f"-> {index_symbol}: Retry {attempt + 1}/{MAX_RETRIES} sau {delay:.1f}s...")
                time.sleep(delay)
            
            # Sử dụng method khác để lấy index data
            stock = vnstock_instance.stock(symbol=index_symbol, source='TCBS')
            df = stock.quote.history(start=START_DATE, end=end_date, interval='1D')
            
            if df is None or df.empty:
                debug_print(f"-> {index_symbol}: Không có dữ liệu")
                continue
            
            # Xử lý dữ liệu tương tự như stock
            required_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                debug_print(f"-> {index_symbol}: Thiếu cột dữ liệu cần thiết")
                continue
            
            df = df[required_columns].copy()
            df.rename(columns={
                'time': 'Date', 'open': 'Open', 'high': 'High', 
                'low': 'Low', 'close': 'Close', 'volume': 'Volume'
            }, inplace=True)
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
            df = df.dropna()
            
            debug_print(f"-> {index_symbol}: Lấy được {len(df)} ngày dữ liệu")
            return df
            
        except Exception as e:
            debug_print(f"-> {index_symbol}: Lỗi attempt {attempt + 1}: {e}")
            if attempt == MAX_RETRIES - 1:
                debug_print(f"-> {index_symbol}: Đã thử hết {MAX_RETRIES} lần")
    
    return pd.DataFrame()

def upload_index_data(s3_client: boto3.client, s3_bucket: str, index_symbol: str, 
                     df: pd.DataFrame, ingest_time: datetime) -> bool:
    """Upload dữ liệu chỉ số thị trường lên S3."""
    try:
        if df.empty:
            return False
        
        # Upload CSV file
        csv_key = f"{S3_INDEX_PATH}/{index_symbol}.csv"
        csv_content = df.to_csv(index=False)
        
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=csv_key,
            Body=csv_content,
            ContentType='text/csv',
            Metadata={
                'index_symbol': index_symbol,
                'record_count': str(len(df)),
                'data_type': 'market_index'
            }
        )
        
        # Upload metadata
        metadata = create_stock_metadata(index_symbol, df, 'vnstock_index', ingest_time)
        metadata_key = f"{S3_METADATA_PATH}/{index_symbol}_metadata.json"
        
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=metadata_key,
            Body=json.dumps(metadata, ensure_ascii=False, indent=2),
            ContentType='application/json'
        )
        
        debug_print(f"✅ [INDEX] {index_symbol}: Đã upload CSV và metadata")
        return True
        
    except Exception as e:
        debug_print(f"❌ [INDEX ERROR] {index_symbol}: {e}")
        return False

# --- [VIẾT LẠI HOÀN TOÀN] Worker để lưu từng file JSON với xử lý lỗi tốt hơn ---
def process_ticker_to_daily_json(ticker: str, ingest_time: datetime, vnstock_instance: Vnstock, s3_bucket: str, s3_client: boto3.client) -> Optional[Dict]:
    """Lấy dữ liệu lịch sử và tải lên S3 dưới dạng các file JSON hàng ngày."""
    # Thêm delay ngẫu nhiên để tránh rate limit
    delay = REQUEST_DELAY_SECONDS + random.uniform(0, 2.0)
    debug_print(f"-> {ticker}: Chờ {delay:.1f}s trước khi xử lý...")
    time.sleep(delay)
    
    df = fetch_vn_ohlcv(vnstock_instance, ticker)
    if df.empty:
        debug_print(f"-> {ticker}: Bỏ qua vì không có dữ liệu.")
        return None

    files_uploaded_count = 0
    files_failed_count = 0
    source = 'vnstock_v3'

    # Lặp qua từng dòng (từng ngày) của DataFrame
    for index, row in df.iterrows():
        try:
            # Tạo S3 key theo cấu trúc mới: bronze/stocks/raw/{ticker}/{ticker}_{date}.json
            day_str = row['Date']
            s3_key = f"{S3_RAW_PATH}/{ticker}/{ticker}_{day_str}.json"
            
            # Tạo nội dung file JSON với validation
            json_payload = {
                'ticker': str(ticker),
                'date': str(row['Date']),
                'open': float(row['Open']) if pd.notna(row['Open']) else None,
                'high': float(row['High']) if pd.notna(row['High']) else None,
                'low': float(row['Low']) if pd.notna(row['Low']) else None,
                'close': float(row['Close']) if pd.notna(row['Close']) else None,
                'volume': int(row['Volume']) if pd.notna(row['Volume']) else 0,
                '_source': source,
                '_ingest_time_utc': ingest_time.isoformat() + 'Z'
            }
            
            # Kiểm tra bucket tồn tại trước khi upload
            for retry in range(MAX_RETRIES):
                try:
                    # Tải file JSON lên S3 với metadata bổ sung
                    s3_client.put_object(
                        Bucket=s3_bucket,
                        Key=s3_key,
                        Body=json.dumps(json_payload, ensure_ascii=False),
                        ContentType='application/json',
                        Metadata={
                            'ticker': ticker,
                            'date': day_str,
                            'source': source
                        }
                    )
                    files_uploaded_count += 1
                    break  # Upload thành công, thoát khỏi retry loop
                    
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == '403':
                        debug_print(f"❌ [LỖI 403] {ticker} ngày {day_str}: Không có quyền truy cập S3")
                        files_failed_count += 1
                        break  # Không retry với lỗi 403
                    elif error_code == 'NoSuchBucket':
                        debug_print(f"❌ [LỖI BUCKET] {ticker}: Bucket {s3_bucket} không tồn tại")
                        return None
                    else:
                        debug_print(f"❌ [LỖI S3] {ticker} ngày {day_str} (retry {retry+1}): {e}")
                        if retry < MAX_RETRIES - 1:
                            time.sleep(exponential_backoff(retry))
                        else:
                            files_failed_count += 1
                            
                except Exception as e:
                    debug_print(f"❌ [LỖI UPLOAD] {ticker} ngày {day_str} (retry {retry+1}): {e}")
                    if retry < MAX_RETRIES - 1:
                        time.sleep(exponential_backoff(retry))
                    else:
                        files_failed_count += 1
                        
        except Exception as e:
            debug_print(f"❌ [LỖI XỬ LÝ DỮ LIỆU] {ticker} ngày {day_str}: {e}")
            files_failed_count += 1
            continue
            
    if files_uploaded_count > 0:
        # Tạo và upload metadata cho cổ phiếu
        metadata = create_stock_metadata(ticker, df, source, ingest_time)
        if metadata:
            upload_stock_metadata(s3_client, s3_bucket, ticker, metadata)
        
        debug_print(f"✅ [THÀNH CÔNG] {ticker}: {files_uploaded_count} files, {files_failed_count} lỗi")
        return {'ticker': ticker, 'files_uploaded': files_uploaded_count, 'files_failed': files_failed_count}
    else:
        debug_print(f"❌ [THẤT BẠI] {ticker}: Không có file nào được upload thành công")
        return None

# --- Hàm Ingestion chính với xử lý lỗi cải thiện ---
def run_stocks_ingestion(tickers: List[str]):
    start_time = time.time()
    ingest_time = datetime.utcnow()
    
    debug_print("=== BẮT ĐẦU QUÁ TRÌNH INGESTION ===")
    debug_print(f"📁 Cấu trúc S3 mới:")
    debug_print(f"   📂 Raw data: {S3_RAW_PATH}/{{ticker}}/{{ticker}}_{{date}}.json")
    debug_print(f"   📂 Metadata: {S3_METADATA_PATH}/{{ticker}}_metadata.json")
    debug_print(f"   📂 Index: {S3_INDEX_PATH}/{{VNINDEX,VN30}}.csv")
    debug_print("")
    
    # Kiểm tra S3 configuration
    s3_bucket = get_s3_bucket_name()
    s3_client = get_s3_client()
    if not s3_bucket or not s3_client:
        debug_print("❌ DỪNG: Không thể lấy tên bucket hoặc khởi tạo S3 client.")
        return

    # Kiểm tra VNStock
    try:
        debug_print("🔄 Đang khởi tạo VNStock instance...")
        vnstock_instance = Vnstock()
        debug_print("✅ VNStock instance khởi tạo thành công.")
    except Exception as e:
        debug_print(f"❌ LỖI NGHIÊM TRỌNG: Không thể khởi tạo Vnstock: {e}")
        return

    unique_tickers = sorted(list(set(tickers)))
    debug_print(f"📊 Sẽ xử lý {len(unique_tickers)} mã cổ phiếu duy nhất...")
    
    successful_tickers, failed_tickers = [], []
    total_files_uploaded = 0
    
    # Chạy tuần tự để tránh rate limit
    debug_print("⚠️ Chạy ở chế độ tuần tự để tránh lỗi Rate Limit.")
    
    for i, ticker in enumerate(unique_tickers, 1):
        try:
            debug_print(f"🔄 [{i}/{len(unique_tickers)}] Đang xử lý mã {ticker}...")
            
            result = process_ticker_to_daily_json(
                ticker, ingest_time, vnstock_instance, s3_bucket, s3_client
            )
            
            if result:
                successful_tickers.append(result)
                total_files_uploaded += result.get('files_uploaded', 0)
                debug_print(f"✅ [{i}/{len(unique_tickers)}] {ticker}: Hoàn thành")
            else:
                failed_tickers.append(ticker)
                debug_print(f"❌ [{i}/{len(unique_tickers)}] {ticker}: Thất bại")
                
            # Progress report mỗi 10 mã
            if i % 10 == 0:
                debug_print(f"📈 TIẾN ĐỘ: {i}/{len(unique_tickers)} mã đã xử lý...")
                
        except KeyboardInterrupt:
            debug_print("⚠️ Người dùng dừng quá trình.")
            break
        except Exception as e:
            debug_print(f"❌ Lỗi nghiêm trọng với mã {ticker}: {e}")
            failed_tickers.append(ticker)

    # Xử lý chỉ số thị trường
    debug_print("\n🔄 Đang xử lý chỉ số thị trường...")
    market_indices = ['VNINDEX', 'VN30']
    
    for index_symbol in market_indices:
        try:
            debug_print(f"🔄 Đang lấy dữ liệu {index_symbol}...")
            index_df = fetch_market_index(vnstock_instance, index_symbol)
            if not index_df.empty:
                upload_index_data(s3_client, s3_bucket, index_symbol, index_df, ingest_time)
            else:
                debug_print(f"❌ Không thể lấy dữ liệu {index_symbol}")
        except Exception as e:
            debug_print(f"❌ Lỗi khi xử lý {index_symbol}: {e}")

    # Báo cáo kết quả
    end_time = time.time()
    debug_print("\n" + "="*50)
    debug_print("📋 BÁO CÁO KẾT QUẢ")
    debug_print("="*50)
    debug_print(f"⏱️  Tổng thời gian: {end_time - start_time:.2f} giây")
    debug_print(f"✅ Mã xử lý thành công: {len(successful_tickers)}")
    debug_print(f"❌ Mã thất bại: {len(failed_tickers)}")
    debug_print(f"📁 Tổng files đã upload: {total_files_uploaded}")
    
    if failed_tickers:
        debug_print(f"📝 Các mã thất bại: {', '.join(failed_tickers[:20])}")
        if len(failed_tickers) > 20:
            debug_print(f"   ... và {len(failed_tickers) - 20} mã khác")
    
    # Success rate
    success_rate = (len(successful_tickers) / len(unique_tickers)) * 100
    debug_print(f"📊 Tỷ lệ thành công: {success_rate:.1f}%")
    
    # Tạo và upload summary metadata
    debug_print("🔄 Đang tạo summary metadata...")
    summary_metadata = create_summary_metadata(
        successful_tickers, failed_tickers, total_files_uploaded, 
        end_time - start_time, ingest_time
    )
    upload_summary_metadata(s3_client, s3_bucket, summary_metadata)
    
    debug_print("="*50)

# --- Điểm khởi chạy Script ---
if __name__ == '__main__':
    vn_tickers_list = [
        # Ngành ngân hàng
        'ABB', 'ACB', 'BAB', 'BID', 'BVB', 'CTG', 'EIB', 'HDB', 'KLB', 'LPB', 
        'MBB', 'MSB', 'NAB', 'NVB', 'OCB', 'PGB', 'SGB', 'SHB', 'SSB', 'STB', 
        'TCB', 'TPB', 'VAB', 'VBB', 'VCB', 'VIB',
        
        # Ngành chứng khoán
        'AGR', 'APG', 'APS', 'ART', 'BSI', 'BVS', 'CTS', 'EVS', 'FTS', 'HBS', 
        'HCM', 'IVS', 'MBS', 'PSI', 'SHS', 'SSI', 'TVB', 'TVS', 'VCI', 'VDS', 
        'VIG', 'VIX', 'VND', 'WSS',
        
        # Ngành điện
        'AVC', 'BHA', 'BSA', 'BTP', 'CHP', 'DHP', 'DNA', 'DNH', 'DRL', 'DTE', 
        'DTK', 'EAD', 'EBA', 'EIC', 'GE2', 'GEG', 'GHC', 'GSM', 'HJS', 'HLE', 
        'HNA', 'HND', 'HPD', 'ISH', 'KHP', 'NBP', 'ND2', 'NED', 'NT2', 'NTH', 
        'PC1', 'PGV', 'PIC', 'POW', 'PPC', 'QPH', 'QTP', 'S4A', 'SBA', 'SBH', 
        'SBM', 'SEB', 'SHP', 'SJD', 'SP2', 'SVH', 'TBC', 'TBD', 'TDB', 'TIC', 
        'TMP', 'TTA', 'TTE', 'TV2', 'VCP', 'VNE', 'VPD', 'VSH',
        
        # Ngành thiết bị điện, điện tử
        'AME', 'BTH', 'CAV', 'CJC', 'DDG', 'EMC', 'EMG', 'GEE', 'GEX', 'HEM', 
        'HLS', 'KIP', 'PPS', 'TGP', 'THI', 'TSB', 'TYA', 'VEC', 'VTH',
        
        # Ngành dầu khí
        'ASP', 'BSR', 'CNG', 'GAS', 'GSP', 'HFC', 'OIL', 'PBK', 'PCG', 'PDT', 
        'PDV', 'PEG', 'PEQ', 'PGC', 'PGD', 'PGS', 'PJC', 'PLC', 'PLX', 'PMG', 
        'POB', 'POS', 'POV', 'PPT', 'PPY', 'PQN', 'PSC', 'PSH', 'PSN', 'PTH', 
        'PTS', 'PTT', 'PTV', 'PTX', 'PVB', 'PVC', 'PVD', 'PVE', 'PVG', 'PVM', 
        'PVP', 'PVS', 'PVT', 'SHE', 'TDG', 'TOS', 'VMG', 'VTO',
        
        # Ngành du lịch và dịch vụ
        'ATS', 'BCV', 'BLN', 'BRS', 'BSC',
        
        # Các mã phổ biến khác
        'VNM', 'FPT', 'HPG', 'VIC', 'MWG', 'SAB', 'VRE', 'TCH', 'VJC', 'MSN',
        'REE', 'VHM', 'BCM', 'GMD', 'PNJ', 'DGC', 'CTD', 'HSG', 'NVL',
        'PDR', 'VPI', 'KDH', 'BWE', 'DXG', 'IJC', 'BCG', 'VGC', 'VCG', 'HNG',
        'DIG', 'SCR', 'QCG', 'TNG', 'FCN', 'ITD', 'VCS', 'VPB'
    ]
    
    # Bắt đầu quá trình ingestion
    debug_print(f"🚀 Bắt đầu crawl dữ liệu cho {len(vn_tickers_list)} mã chứng khoán VN")
    run_stocks_ingestion(vn_tickers_list)