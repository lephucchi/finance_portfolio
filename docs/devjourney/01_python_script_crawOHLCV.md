# 📅 Development Journal - Day 01
**Date:** September 20, 2025  
**Focus:** Vietnamese Banking Stocks OHLCV Data Pipeline Development

## 🎯 Objective
Phát triển script Python để crawl dữ liệu OHLCV (Open, High, Low, Close, Volume) hàng ngày cho các cổ phiếu ngân hàng Việt Nam và upload lên AWS S3 bucket, chuẩn bị cho việc tích hợp vào Airflow DAGs.

## 📋 Tasks Completed

### 1. 🔍 Phân tích Jupyter Notebook hiện có
- **File:** `data/jupyter_files/VN_stock_OHLC_craw.ipynb`
- **Findings:**
  - Sử dụng thư viện `vnstock` để crawl dữ liệu từ nguồn VCI
  - Danh sách 27 mã cổ phiếu ngân hàng Việt Nam
  - Logic retry với error handling cho API calls
  - Xử lý dữ liệu với pandas để format OHLCV

### 2. 🔧 Phân tích script hiện tại
- **File:** `scripts/ingest_stock.py`
- **Current State:**
  - Cấu hình AWS S3 cơ bản
  - Logic upload đơn giản
  - Chỉ demo với API Vietstock (không hoạt động)

### 3. 🚀 Redesign & Implementation

#### A. Cấu trúc dữ liệu mới
```json
{
  "symbol": "VCB",
  "date": "2024-09-19",
  "open": 60.87,
  "high": 61.34,
  "low": 60.8,
  "close": 61.2,
  "volume": 1346904,
  "timestamp": "2025-09-20T11:24:25.684420"
}
```

#### B. S3 Partition Strategy
```
s3://bankanalystportfolio/raw/ohlcv/{SYMBOL}/date={YYYY-MM-DD}/{SYMBOL}_{YYYY-MM-DD}.json
```

**Example:**
```
s3://bankanalystportfolio/raw/ohlcv/VCB/date=2024-09-19/VCB_2024-09-19.json
```

#### C. Core Functions Implemented

##### `get_stock_data_daily(symbol, target_date, retries=3, delay=5)`
- Crawl dữ liệu OHLCV cho một mã cổ phiếu trong ngày cụ thể
- Retry logic với exponential backoff
- Error handling và logging chi tiết
- Data validation và type conversion

##### `upload_to_s3(data, key)`
- Upload JSON data lên S3 với fallback local storage
- Error handling và retry mechanism
- Support cho test mode khi AWS credentials không có

##### `crawl_banking_stocks_ohlcv(target_date)`
- Crawl tất cả 27 mã cổ phiếu ngân hàng
- Progress tracking và statistics
- Rate limiting để tránh bị block

##### `test_s3_connection()`
- Validate AWS credentials và S3 permissions
- Debug helper cho troubleshooting

### 4. 🏦 Banking Stocks Coverage
```python
BANKING_STOCKS = [
    'ABB', 'ACB', 'BAB', 'BID', 'BVB', 'CTG', 'EIB', 'HDB', 
    'KLB', 'LPB', 'MBB', 'MSB', 'NAB', 'NVB', 'OCB', 'PGB', 
    'SGB', 'SHB', 'SSB', 'STB', 'TCB', 'TPB', 'VAB', 'VBB', 
    'VCB', 'VIB', 'VPB'
]
```

### 5. 🛠️ CLI Interface
```bash
# Crawl tất cả banking stocks cho ngày hiện tại
python scripts/ingest_stock.py

# Crawl cho ngày cụ thể
python scripts/ingest_stock.py --date 2024-09-19

# Crawl cho một mã cụ thể
python scripts/ingest_stock.py --symbol VCB --date 2024-09-19

# Test S3 connection
python scripts/ingest_stock.py --test-s3
```

### 6. 📦 Dependencies Updated
Added to `requirements.txt`:
```
vnstock==0.2.9.6          # Vietnam stock market data
```

## 🔧 Technical Details

### Error Handling Strategy
1. **API Level:** Retry với delay increasing (5s, 10s, 15s)
2. **S3 Level:** Fallback to local storage nếu upload fail
3. **Data Level:** Validation và type conversion safety

### AWS Integration
- Support multiple environment variable formats:
  - `AWS_DEFAULT_REGION` hoặc `AWS_REGION`
  - `S3_BUCKET` hoặc `AWS_BUCKET_NAME`
- Graceful degradation khi credentials không có
- Test mode với local file storage

### Data Quality
- Timestamp cho traceability
- JSON format với proper encoding
- Partition structure compatible với Apache Spark/Hive

## 🎯 Testing Results

### Single Stock Test
```bash
python scripts/ingest_stock.py --symbol VCB --date 2024-09-19
```
**Result:** ✅ Successfully crawled và lưu dữ liệu VCB

### S3 Connection Test
```bash
python scripts/ingest_stock.py --test-s3
```
**Result:** ⚠️ 403 Forbidden - cần update AWS permissions

## 🔄 Next Steps (Day 02)
1. **AWS Permissions:** Fix S3 bucket permissions cho production upload
2. **Airflow Integration:** Convert script thành Airflow DAG
3. **Monitoring:** Add logging và alerting
4. **Scheduling:** Setup daily cron job
5. **Data Validation:** Add quality checks cho crawled data

## 🏗️ Architecture Overview
```
[vnstock API] → [Python Script] → [S3 Bucket] → [Future: Airflow DAG]
     ↓              ↓               ↓
[Stock Data] → [JSON Format] → [Partitioned Storage]
```

## 📊 Success Metrics
- ✅ Script hoạt động với 27 banking stocks
- ✅ Proper error handling và retry logic
- ✅ CLI interface hoàn chỉnh
- ✅ Fallback mechanism hoạt động
- ⚠️ S3 upload cần fix permissions

---
**Next Review:** Day 02 - AWS Integration & Airflow DAG Development