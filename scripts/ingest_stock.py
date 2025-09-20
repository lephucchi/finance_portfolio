import os
import sys
from dotenv import load_dotenv
import boto3
import requests
import datetime
import pandas as pd
import time
import json
from vnstock import Vnstock

# Add utils to path for logging
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from logger import log_ohlcv_execution

# Load secrets từ file .env
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET") or os.getenv("AWS_BUCKET_NAME")

print(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET)

# Danh sách các mã cổ phiếu ngân hàng
BANKING_STOCKS = [
    'ABB',  # An Binh Bank
    'ACB',  # Ngân hàng Á Châu
    'BAB',  # Bac A Bank
    'BID',  # BIDV
    'BVB',  # BVBank
    'CTG',  # Vietinbank
    'EIB',  # Eximbank
    'HDB',  # HD Bank
    'KLB',  # KienlongBank
    'LPB',  # LPBank
    'MBB',  # MB Bank
    'MSB',  # MSB
    'NAB',  # Nam A Bank
    'NVB',  # NCB
    'OCB',  # OCB
    'PGB',  # PGbank
    'SGB',  # Saigon Bank
    'SHB',  # SHB
    'SSB',  # SeABank
    'STB',  # Sacombank
    'TCB',  # Techcombank
    'TPB',  # TPBank
    'VAB',  # VietABank
    'VBB',  # Vietbank
    'VCB',  # Vietcombank
    'VIB',  # VIB
    'VPB'   # VPBank
]

s3_client = None
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_REGION:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
else:
    print("⚠️  AWS credentials chưa được cấu hình đầy đủ. Script sẽ chạy ở mode test (lưu file local).")

def test_s3_connection():
    """Test S3 connection and permissions"""
    if not s3_client or not S3_BUCKET:
        return False
    
    try:
        # Test by trying to list objects (less restrictive than head_bucket)
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=1)
        print(f"✅ S3 connection successful to bucket: {S3_BUCKET}")
        return True
    except Exception as e:
        print(f"❌ S3 connection failed: {e}")
        print(f"💡 Có thể do: credentials hết hạn, không có quyền truy cập bucket, hoặc bucket không tồn tại")
        return False

def upload_to_s3(data: str, key: str):
    """Upload dữ liệu lên S3 bucket"""
    try:
        if S3_BUCKET is None or s3_client is None:
            print(f"⚠️  S3 chưa được cấu hình. Sẽ lưu file local thay thế.")
            # Tạo thư mục local để test
            local_path = f"/tmp/{key}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"💾 Đã lưu file local: {local_path}")
            return True
            
        # Đảm bảo data là string
        if not isinstance(data, str):
            data = str(data)
            
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=data.encode("utf-8"),
            ContentType='application/json'
        )
        return True
    except Exception as e:
        print(f"❌ Lỗi khi upload {key} lên S3: {e}")
        print(f"⚠️  Đang fallback về local storage...")
        
        # Fallback to local storage
        try:
            local_path = f"/tmp/{key}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"💾 Đã lưu file local: {local_path}")
            return True
        except Exception as local_e:
            print(f"❌ Lỗi cả local storage: {local_e}")
            return False

def get_stock_data_daily(symbol: str, target_date: str = None, retries: int = 3, delay: int = 5):
    """
    Lấy dữ liệu OHLCV cho một mã cổ phiếu trong một ngày cụ thể
    
    Args:
        symbol: Mã cổ phiếu (VD: 'VCB')
        target_date: Ngày cần lấy dữ liệu (format: 'YYYY-MM-DD'), None = hôm nay
        retries: Số lần thử lại khi có lỗi
        delay: Thời gian chờ giữa các lần thử (giây)
    
    Returns:
        dict hoặc None nếu có lỗi
    """
    if target_date is None:
        target_date = datetime.date.today().strftime("%Y-%m-%d")
    
    start_time = time.time()
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    
    for attempt in range(retries):
        try:
            # Lấy dữ liệu cho ngày cụ thể (có thể cần lấy range để đảm bảo có dữ liệu)
            df = stock.quote.history(start=target_date, end=target_date, interval='1D')
            
            if df.empty:
                error_msg = f"Không có dữ liệu cho {symbol} ngày {target_date}"
                print(f"⚠️  {error_msg}")
                
                # Log failed attempt
                log_ohlcv_execution(
                    symbol=symbol,
                    target_date=target_date,
                    status="failed",
                    error=error_msg,
                    details={
                        "execution_time_seconds": time.time() - start_time,
                        "attempts": attempt + 1,
                        "reason": "no_data_available"
                    }
                )
                return None
            
            # Xử lý dữ liệu
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
            
            # Lấy dữ liệu OHLCV
            ohlcv_data = df[['open', 'high', 'low', 'close', 'volume']].iloc[-1]
            
            # Tạo dict với thông tin cần thiết
            result = {
                'symbol': symbol,
                'date': target_date,
                'open': float(ohlcv_data['open']),
                'high': float(ohlcv_data['high']),
                'low': float(ohlcv_data['low']),
                'close': float(ohlcv_data['close']),
                'volume': int(ohlcv_data['volume']),
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            # Log successful execution
            log_ohlcv_execution(
                symbol=symbol,
                target_date=target_date,
                status="success",
                details={
                    "execution_time_seconds": time.time() - start_time,
                    "attempts": attempt + 1,
                    "data_quality": "complete",
                    "ohlcv_summary": {
                        "open": result['open'],
                        "close": result['close'],
                        "volume": result['volume']
                    }
                }
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Lỗi khi lấy dữ liệu cho {symbol} (lần {attempt+1}/{retries}): {e}"
            print(f"⚠️  {error_msg}")
            
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                # Log final failure
                log_ohlcv_execution(
                    symbol=symbol,
                    target_date=target_date,
                    status="failed",
                    error=str(e),
                    details={
                        "execution_time_seconds": time.time() - start_time,
                        "attempts": retries,
                        "reason": "api_error"
                    }
                )
                print(f"❌ Không thể lấy dữ liệu cho {symbol} sau {retries} lần thử")
                return None

def crawl_banking_stocks_ohlcv(target_date: str = None):
    """
    Crawl dữ liệu OHLCV cho tất cả cổ phiếu ngân hàng và upload lên S3
    
    Args:
        target_date: Ngày cần crawl (format: 'YYYY-MM-DD'), None = hôm nay
    """
    if target_date is None:
        target_date = datetime.date.today().strftime("%Y-%m-%d")
    
    print(f"🚀 Bắt đầu crawl dữ liệu OHLCV cho {len(BANKING_STOCKS)} cổ phiếu ngân hàng ngày {target_date}")
    
    start_time = time.time()
    successful_uploads = 0
    failed_uploads = 0
    successful_symbols = []
    failed_symbols = []
    
    for symbol in BANKING_STOCKS:
        print(f"📊 Đang xử lý {symbol}...")
        
        # Lấy dữ liệu OHLCV
        stock_data = get_stock_data_daily(symbol, target_date)
        
        if stock_data:
            # Tạo key cho S3 theo pattern partition
            s3_key = f"raw/ohlcv/{symbol}/date={target_date}/{symbol}_{target_date}.json"
            
            # Convert sang JSON
            json_data = json.dumps(stock_data, ensure_ascii=False, indent=2)
            
            # Upload lên S3
            if upload_to_s3(json_data, s3_key):
                print(f"✅ Đã upload {symbol} lên S3: {s3_key}")
                successful_uploads += 1
                successful_symbols.append(symbol)
            else:
                failed_uploads += 1
                failed_symbols.append(symbol)
        else:
            failed_uploads += 1
            failed_symbols.append(symbol)
        
        # Nghỉ ngắn để tránh rate limit
        time.sleep(1)
    
    execution_time = time.time() - start_time
    
    print(f"\n📈 Kết quả crawl:")
    print(f"   ✅ Thành công: {successful_uploads}/{len(BANKING_STOCKS)}")
    print(f"   ❌ Thất bại: {failed_uploads}/{len(BANKING_STOCKS)}")
    
    # Log overall execution
    status = "success" if failed_uploads == 0 else ("partial" if successful_uploads > 0 else "failed")
    log_ohlcv_execution(
        symbol="all_stocks",
        target_date=target_date,
        status=status,
        details={
            "total_stocks": len(BANKING_STOCKS),
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "execution_time_seconds": execution_time,
            "successful_symbols": successful_symbols,
            "failed_symbols": failed_symbols,
            "success_rate": (successful_uploads / len(BANKING_STOCKS)) * 100
        }
    )
    
    return successful_uploads, failed_uploads

if __name__ == "__main__":
    import argparse
    
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Crawl OHLCV data cho cổ phiếu ngân hàng Việt Nam')
    parser.add_argument('--date', type=str, help='Ngày cần crawl (YYYY-MM-DD), mặc định là hôm nay')
    parser.add_argument('--symbol', type=str, help='Crawl cho một mã cụ thể thay vì tất cả')
    parser.add_argument('--test-s3', action='store_true', help='Chỉ test S3 connection')
    
    args = parser.parse_args()
    
    # Nếu chỉ test S3
    if args.test_s3:
        print(f"🔧 Testing S3 connection...")
        print(f"AWS_ACCESS_KEY_ID: {'✅ Set' if AWS_ACCESS_KEY_ID else '❌ Not set'}")
        print(f"AWS_SECRET_ACCESS_KEY: {'✅ Set' if AWS_SECRET_ACCESS_KEY else '❌ Not set'}")
        print(f"AWS_REGION: {AWS_REGION}")
        print(f"S3_BUCKET: {S3_BUCKET}")
        
        if s3_client and S3_BUCKET:
            test_s3_connection()
        else:
            print("❌ S3 client not initialized")
        exit(0)
    
    target_date = args.date
    if target_date is None:
        target_date = datetime.date.today().strftime("%Y-%m-%d")
    
    print(f"🏦 VN Banking Stocks OHLCV Crawler")
    print(f"📅 Target date: {target_date}")
    print(f"☁️  S3 Bucket: {S3_BUCKET}")
    
    # Test S3 connection nếu có cấu hình
    if S3_BUCKET and s3_client:
        s3_connected = test_s3_connection()
        if not s3_connected:
            print("⚠️  S3 connection failed. Script sẽ chạy ở local mode.")
    
    print("=" * 50)
    
    if args.symbol:
        # Crawl cho một mã cụ thể
        if args.symbol.upper() in BANKING_STOCKS:
            print(f"📊 Crawling data for {args.symbol.upper()}...")
            stock_data = get_stock_data_daily(args.symbol.upper(), target_date)
            
            if stock_data:
                s3_key = f"raw/ohlcv/{args.symbol.upper()}/date={target_date}/{args.symbol.upper()}_{target_date}.json"
                json_data = json.dumps(stock_data, ensure_ascii=False, indent=2)
                
                if upload_to_s3(json_data, s3_key):
                    print(f"✅ Uploaded {args.symbol.upper()} to S3: {s3_key}")
                else:
                    print(f"❌ Failed to upload {args.symbol.upper()}")
            else:
                print(f"❌ Failed to get data for {args.symbol.upper()}")
        else:
            print(f"❌ {args.symbol.upper()} không có trong danh sách banking stocks")
    else:
        # Crawl cho tất cả banking stocks
        successful, failed = crawl_banking_stocks_ohlcv(target_date)
        
        if failed == 0:
            print(f"\n🎉 Crawl hoàn thành thành công!")
        else:
            print(f"\n⚠️  Crawl hoàn thành với {failed} lỗi")
            
    print("=" * 50)
    print("✨ Script completed!")
