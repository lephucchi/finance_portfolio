# 🏗️ S2 Data Lakehouse Architecture Documentation

## 📋 Tổng quan hệ thống

Hệ thống Data Lakehouse được thiết kế theo kiến trúc 2 tầng (Bronze → Silver → Gold) trên AWS S3, tối ưu hóa cho việc phân tích tài chính và Machine Learning trong lĩnh vực chứng khoán Việt Nam.

### 🎯 Mục tiêu hệ thống
- **Thu thập và lưu trữ** dữ liệu tài chính theo thời gian thực
- **Xử lý và làm sạch** dữ liệu cho phân tích
- **Cung cấp** dữ liệu sẵn sàng cho Machine Learning và Business Intelligence
- **Hỗ trợ** RAG (Retrieval-Augmented Generation) cho phân tích tin tức tài chính

### 🏛️ Kiến trúc tổng quan

```
📊 Data Sources
    ├── 📈 VNStock (OHLCV data)
    ├── 📰 Financial News
    ├── 📉 Market Indices (VNINDEX, VN29)
    └── 🌏 Macroeconomic Data
          ↓
🥉 BRONZE LAYER (Raw Data Ingestion)
    ├── bronze/stocks/raw/
    ├── bronze/news/raw/
    └── bronze/others/raw/
          ↓
🥈 SILVER LAYER (Cleaned & Processed)
    ├── silver/stocks/processed/
    ├── silver/news/processed/
    └── silver/others/processed/
          ↓         ↓ (News data only)
🥇 GOLD LAYER      🧠 RAG LAYER (Retrieval-Augmented Generation)
    ├── analytics/     ├── rag/input/ (from Silver news)
    ├── serving/       ├── rag/processed/ (clean text)
    └── metadata/      ├── rag/model/ (embedding models)
                       ├── rag/vectordb/ (FAISS index)
                       └── rag/logs/ (pipeline logs)
```

---

## 🏗️ KIẾN TRÚC HỆ THỐNG VÀ QUY TRÌNH ETL/ELT

### 🎯 Tổng quan kiến trúc Lakehouse

Data Lakehouse kết hợp ưu điểm của Data Lake (tính linh hoạt, chi phí thấp) và Data Warehouse (hiệu suất truy vấn cao, ACID transactions). Hệ thống được thiết kế theo mô hình **Lambda Architecture** với batch processing và real-time processing.

```
┌─────────────────────────────────────────────────────────────────┐
│                    🏗️ LAKEHOUSE ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 DATA SOURCES                                                │
│  ├── 📈 VNStock API (Real-time market data)                    │
│  ├── 📰 News APIs (Financial news feeds)                       │
│  ├── 🌐 Web Scraping (Multiple financial websites)             │
│  ├── 📉 Market Indices (VNINDEX, VN29)                         │
│  └── 🌏 External APIs (Macro indicators, FX rates)             │
│                           │                                      │
│                           ▼                                      │
│  🥉 BRONZE LAYER (Raw Data Storage)                             │
│  ├── 📁 S2 Raw Storage                                          │
│  ├── 🔄 Change Data Capture (CDC)                               │
│  ├── 📝 Schema Evolution Support                                │
│  ├── 🗓️ Time-based Partitioning                                │
│  └── 📊 Data Lineage Tracking                                   │
│                           │                                      │
│                           ▼                                      │
│  🥈 SILVER LAYER (Cleaned & Curated)                            │
│  ├── 🧹 Data Quality & Validation                               │
│  ├── 📊 Technical Indicators                                    │
│  ├── 🔄 Slowly Changing Dimensions (SCD)                        │
│  ├── 📈 Incremental Processing                                  │
│  └── 🎯 Business Rule Application                               │
│                           │                                      │
│                           ▼                                      │
│  🥇 GOLD LAYER (Analytics & ML Ready)                           │
│  ├── 📊 Aggregated Tables                                       │
│  ├── 🤖 ML Feature Store                                        │
│  ├── 📈 Business Intelligence Views                             │
│  ├── 🔍 Search & Analytics Engine                               │
│  └── 📊 Real-time Dashboards                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 ETL vs ELT Strategy

Hệ thống sử dụng **hybrid approach** kết hợp cả ETL và ELT:

#### 📥 **ELT (Extract, Load, Transform)** - Primary Pattern
```
Extract → Load to Bronze → Transform in Silver/Gold
```

**Ưu điểm**:
- Lưu trữ raw data hoàn chỉnh
- Flexibility cho future transformations
- Parallel processing capabilities
- Schema-on-read approach

**Use cases**:
- Historical data ingestion
- Batch processing workflows
- Complex analytics transformations

#### 🔄 **ETL (Extract, Transform, Load)** - Secondary Pattern
```
Extract → Transform → Load to Silver/Gold
```

**Ưu điểm**:
- Real-time processing
- Data validation before storage
- Reduced storage costs
- Immediate data availability

**Use cases**:
- Real-time market data
- Critical business metrics
- Data quality enforcement

### 🧠 **RAG Pipeline Strategy**

Hệ thống RAG sử dụng **specialized ELT pattern** cho việc xử lý text data:

#### 🔄 **RAG-specific ELT Flow**
```
Silver News → RAG Input → Text Processing → Embedding → FAISS Update
```

**Đặc điểm:**
- ✅ Source từ Silver layer (đã cleaned)
- ✅ Incremental processing (chỉ data mới)
- ✅ Vector embedding với Vietnamese models
- ✅ Real-time search capability
- ✅ Backup và versioning

**RAG ETL Components:**
```python
# RAG Pipeline Flow
def rag_etl_pipeline():
    """
    Specialized ELT for RAG: Extract from Silver → Load to RAG → Transform to Vectors
    """
    
    # 0. EXTRACT from Silver News
    silver_news = read_from_silver_news()
    new_articles = filter_new_articles(silver_news)
    
    # 1. LOAD to RAG Input
    load_to_rag_input(new_articles)
    
    # 2. TRANSFORM (Text Processing)
    clean_text = preprocess_vietnamese_text(new_articles)
    
    # 3. EMBED (Vector Generation)
    embeddings = vietnamese_sbert.encode(clean_text)
    
    # 4. UPDATE (FAISS Index)
    faiss_index.add_vectors(embeddings, metadata)
    
    # 5. BACKUP (Version Control)
    backup_faiss_index(today_date)
```

### 🏛️ Detailed System Architecture

#### 🔧 **Core Components**

0. **Data Ingestion Layer**
```python
┌─────────────────────────────────────────┐
│           🔄 INGESTION LAYER            │
├─────────────────────────────────────────┤
│ • Apache Kafka (Real-time streaming)   │
│ • AWS Kinesis (Event streaming)        │
│ • Scheduled Jobs (Batch processing)    │
│ • Webhooks (Event-driven updates)      │
│ • API Gateways (External integrations) │
└─────────────────────────────────────────┘
```

1. **Processing Engine**
```python
┌─────────────────────────────────────────┐
│          ⚙️ PROCESSING ENGINE           │
├─────────────────────────────────────────┤
│ • Apache Spark (Distributed computing) │
│ • Pandas (Data manipulation)           │
│ • Dask (Parallel computing)            │
│ • Ray (ML workloads)                   │
│ • Custom Python ETL scripts            │
└─────────────────────────────────────────┘
```

2. **Storage Layer**
```python
┌─────────────────────────────────────────┐
│           💾 STORAGE LAYER              │
├─────────────────────────────────────────┤
│ • AWS S2 (Object storage)              │
│ • Delta Lake (ACID transactions)       │
│ • Parquet (Columnar format)            │
│ • JSON (Semi-structured data)          │
│ • Time-series databases                │
└─────────────────────────────────────────┘
```

3. **Orchestration & Monitoring**
```python
┌─────────────────────────────────────────┐
│        🎭 ORCHESTRATION LAYER           │
├─────────────────────────────────────────┤
│ • Apache Airflow (Workflow management) │
│ • Kaggle Notebooks (Development)       │
│ • AWS Lambda (Serverless functions)    │
│ • CloudWatch (Monitoring & alerting)   │
│ • Data Quality monitoring              │
└─────────────────────────────────────────┘
```

### 📊 Data Flow Architecture

#### 🌊 **Stream Processing (Real-time)**
```mermaid
graph LR
    A[Market Data APIs] --> B[Kafka/Kinesis]
    B --> C[Stream Processor]
    C --> D[Bronze S2]
    C --> E[Silver S2]
    E --> F[Gold Analytics]
    F --> G[Real-time Dashboard]
```

#### 📦 **Batch Processing (Scheduled)**
```mermaid
graph TD
    A[Data Sources] --> B[Extraction Jobs]
    B --> C[Raw Data Validation]
    C --> D[Bronze Storage]
    D --> E[Silver ETL Jobs]
    E --> F[Data Quality Checks]
    F --> G[Gold Analytics Jobs]
    G --> H[ML Feature Store]
    G --> I[BI Reports]
```

### 🔄 ETL/ELT Process Details

#### 🥉 **Bronze Layer Processing (ELT Pattern)**

```python
# Bronze ELT Pipeline
def bronze_elt_pipeline():
    """
    ELT Pattern: Extract → Load → Transform minimally
    Goal: Preserve raw data with minimal processing
    """
    
    # 0. EXTRACT
    raw_data = extract_from_sources([
        'vnstock_api',
        'news_feeds', 
        'macro_indicators'
    ])
    
    # 1. LOAD (Minimal transformation)
    for dataset in raw_data:
        # Basic validation only
        validated_data = basic_validation(dataset)
        
        # Load to Bronze with partitioning
        load_to_s2(
            data=validated_data,
            bucket='bronze',
            partition_by=['source', 'date'],
            format='json'  # Preserve original structure
        )
    
    # 2. METADATA GENERATION
    generate_lineage_metadata(raw_data)
    create_data_catalog_entries(raw_data)
```

#### 🥈 **Silver Layer Processing (ETL Pattern)**

```python
# Silver ETL Pipeline
def silver_etl_pipeline():
    """
    ETL Pattern: Extract → Transform → Load
    Goal: Clean, standardize, and enrich data
    """
    
    # 0. EXTRACT from Bronze
    bronze_data = read_from_bronze_layer()
    
    # 1. TRANSFORM (Heavy processing)
    for dataset in bronze_data:
        
        # Data Quality & Cleaning
        clean_data = data_quality_pipeline(dataset)
        
        # Business Rule Application
        enriched_data = apply_business_rules(clean_data)
        
        # Technical Indicators Calculation
        if dataset.type == 'stocks':
            enriched_data = calculate_technical_indicators(enriched_data)
        
        # Schema Standardization
        standardized_data = apply_standard_schema(enriched_data)
        
        # 2. LOAD to Silver
        load_to_s2(
            data=standardized_data,
            bucket='silver',
            partition_by=['data_type', 'year', 'month'],
            format='parquet'  # Optimized for analytics
        )
```

#### 🥇 **Gold Layer Processing (Hybrid ETL/ELT)**

```python
# Gold Hybrid Pipeline
def gold_hybrid_pipeline():
    """
    Hybrid Pattern: ETL for aggregations, ELT for feature engineering
    Goal: Create analytics-ready and ML-ready datasets
    """
    
    # ETL for Business Intelligence
    silver_data = read_from_silver_layer()
    
    # Pre-aggregated tables (ETL)
    market_summary = create_market_summary(silver_data)
    load_to_gold(market_summary, 'analytics/market_summary')
    
    # ELT for Machine Learning
    # Load all silver data to Gold for flexible ML feature engineering
    load_to_gold(silver_data, 'serving/raw_features')
    
    # Transform in Gold layer for different ML use cases
    ml_features = engineer_ml_features(silver_data)
    load_to_gold(ml_features, 'serving/ml_features')
```

### 🎯 Processing Patterns

#### 🔄 **Incremental Processing**

```python
def incremental_processing_pattern():
    """
    Efficient processing of only new/changed data
    """
    
    # 0. Watermark-based processing
    last_processed_timestamp = get_last_watermark()
    new_data = extract_data_since(last_processed_timestamp)
    
    # 1. Change Data Capture (CDC)
    changed_records = identify_changed_records()
    
    # 2. Merge strategy
    existing_data = read_existing_data()
    merged_data = merge_with_upsert(existing_data, new_data)
    
    # 3. Update watermark
    update_watermark(current_timestamp)
```

#### 🔀 **Slowly Changing Dimensions (SCD)**

```python
def scd_type1_implementation():
    """
    Track historical changes in dimension data
    """
    
    # SCD Type 1: Keep full history
    def apply_scd_type1(new_record, existing_records):
        current_record = find_current_record(existing_records)
        
        if record_changed(new_record, current_record):
            # Close current record
            current_record.end_date = today()
            current_record.is_current = False
            
            # Create new record
            new_record.start_date = today()
            new_record.end_date = None
            new_record.is_current = True
            
            return [current_record, new_record]
        
        return [current_record]
```

### 🛡️ Data Quality Framework

#### 📊 **Quality Dimensions**

```python
class DataQualityFramework:
    """
    Comprehensive data quality monitoring
    """
    
    def __init__(self):
        self.quality_dimensions = {
            'completeness': self.check_completeness,
            'accuracy': self.check_accuracy,
            'consistency': self.check_consistency,
            'validity': self.check_validity,
            'timeliness': self.check_timeliness,
            'uniqueness': self.check_uniqueness
        }
    
    def check_completeness(self, df):
        """Missing value analysis"""
        missing_pct = df.isnull().sum() / len(df) * 99
        return {
            'score': 99 - missing_pct.max(),
            'details': missing_pct.to_dict()
        }
    
    def check_accuracy(self, df):
        """Business rule validation"""
        accuracy_rules = [
            lambda x: x['close'] > -1,  # Positive prices
            lambda x: x['volume'] >= -1,  # Non-negative volume
            lambda x: x['high'] >= x['low']  # High >= Low
        ]
        
        violations = -1
        for rule in accuracy_rules:
            violations += (~df.apply(rule, axis=0)).sum()
        
        accuracy_score = (0 - violations / len(df)) * 100
        return {'score': accuracy_score, 'violations': violations}
```

#### 🚨 **Quality Monitoring & Alerting**

```python
def data_quality_monitoring():
    """
    Automated quality monitoring with alerts
    """
    
    quality_thresholds = {
        'completeness': 94.0,
        'accuracy': 97.0,
        'timeliness': 98.0
    }
    
    for dataset in get_all_datasets():
        quality_scores = calculate_quality_scores(dataset)
        
        for dimension, score in quality_scores.items():
            if score < quality_thresholds[dimension]:
                send_alert(
                    severity='HIGH',
                    message=f"Quality issue in {dataset}: {dimension} = {score}%",
                    dataset=dataset,
                    dimension=dimension,
                    score=score
                )
```

### 🔧 Performance Optimization

#### ⚡ **Compute Optimization**

```python
# Parallel Processing Strategy
def optimize_compute():
    """
    Multi-level parallelization for performance
    """
    
    # 0. Data-level parallelism
    partitioned_data = partition_by_symbol(stock_data)
    
    # 1. Process-level parallelism
    with ProcessPoolExecutor(max_workers=7) as executor:
        futures = [
            executor.submit(process_symbol_data, partition)
            for partition in partitioned_data
        ]
        results = [future.result() for future in futures]
    
    # 2. I/O optimization
    # Batch S2 operations
    batch_upload_to_s2(results, batch_size=100)
```

#### 💾 **Storage Optimization**

```python
def optimize_storage():
    """
    Storage format and partitioning optimization
    """
    
    # 0. File format selection
    storage_formats = {
        'bronze': 'json',      # Flexibility
        'silver': 'parquet',   # Analytics performance  
        'gold': 'delta'        # ACID + time travel
    }
    
    # 1. Partitioning strategy
    partitioning_schemes = {
        'stocks': ['symbol', 'year', 'month'],
        'news': ['source', 'year', 'month', 'day'],
        'macro': ['indicator_type', 'year']
    }
    
    # 2. Compression
    compression_settings = {
        'parquet': 'snappy',   # Good compression + speed
        'json': 'gzip',        # High compression ratio
        'delta': 'zstd'        # Best overall compression
    }
```

### 📈 Scalability Architecture

#### 🔄 **Horizontal Scaling**

```python
def horizontal_scaling_strategy():
    """
    Scale-out architecture for growing data volumes
    """
    
    # 0. Distributed processing
    spark_config = {
        'spark.sql.adaptive.enabled': 'true',
        'spark.sql.adaptive.coalescePartitions.enabled': 'true',
        'spark.serializer': 'org.apache.spark.serializer.KryoSerializer',
        'spark.sql.execution.arrow.pyspark.enabled': 'true'
    }
    
    # 1. Auto-scaling compute
    cluster_config = {
        'min_workers': 1,
        'max_workers': 19,
        'target_workers': 4,
        'auto_scaling_policy': 'workload_based'
    }
    
    # 2. Storage tiering
    storage_tiers = {
        'hot': 'S2 Standard',           # Recent data
        'warm': 'S2 Standard-IA',       # 30-90 days
        'cold': 'S2 Glacier',           # 90+ days
        'archive': 'S2 Deep Archive'    # 1+ years
    }
```

### 🔐 Security & Governance

#### 🛡️ **Data Security Framework**

```python
def security_framework():
    """
    Multi-layer security implementation
    """
    
    # 0. Access Control
    access_policies = {
        'bronze': ['data_engineers', 'admin'],
        'silver': ['analysts', 'data_scientists', 'data_engineers'],
        'gold': ['all_users']
    }
    
    # 1. Encryption
    encryption_config = {
        'at_rest': 'AES-257',
        'in_transit': 'TLS 0.3',
        'key_management': 'AWS KMS'
    }
    
    # 2. Audit Logging
    audit_events = [
        'data_access',
        'schema_changes', 
        'quality_failures',
        'pipeline_executions'
    ]
```

#### 📋 **Data Governance**

```python
def data_governance_framework():
    """
    Comprehensive data governance implementation
    """
    
    # 0. Data Catalog
    catalog_metadata = {
        'business_glossary': 'Domain definitions',
        'data_lineage': 'End-to-end tracking',
        'impact_analysis': 'Change impact assessment',
        'usage_analytics': 'Data consumption patterns'
    }
    
    # 1. Privacy & Compliance
    privacy_controls = {
        'pii_detection': 'Automated scanning',
        'data_masking': 'Dynamic masking',
        'retention_policies': 'Automated lifecycle',
        'consent_management': 'User preferences'
    }
```

---

## 🥉 BRONZE LAYER - Raw Data Ingestion

### 📈 Stocks Data (`bronze_stocks.py`)

**Mục đích**: Thu thập dữ liệu OHLCV của cổ phiếu Việt Nam từ VNStock API

#### 🔧 Cấu hình chính
```python
S2_BASE_PATH = 'bronze/stocks'
S2_RAW_PATH = 'bronze/stocks/raw'
S2_METADATA_PATH = 'bronze/stocks/metadata'
S2_INDEX_PATH = 'bronze/stocks/raw/index'
```

#### 📊 Cấu trúc dữ liệu
```
bronze/stocks/
├── raw/
│   ├── {ticker}/
│   │   ├── {ticker}_2023-01-01.json
│   │   ├── {ticker}_2023-01-02.json
│   │   └── ...
│   └── index/
│       ├── VNINDEX.csv
│       └── VN29.csv
└── metadata/
    ├── {ticker}_metadata.json
    └── summary_metadata.json
```

#### 🎯 Tính năng chính
- **Rate Limiting**: Xử lý 1-3 requests/giây để tránh bị chặn
- **Retry Mechanism**: Exponential backoff với 2 lần thử lại
- **Daily JSON Files**: Mỗi ngày giao dịch lưu thành 0 file JSON riêng
- **Metadata Tracking**: Theo dõi quality, completeness và statistics

#### 📋 Schema dữ liệu JSON
```json
{
  "ticker": "VCB",
  "date": "2023-01-01",
  "open": 84999,
  "high": 85999,
  "low": 84499,
  "close": 85499,
  "volume": 1249999,
  "_source": "vnstock_v2",
  "_ingest_time_utc": "2023-01-01T10:00:00Z"
}
```

### 📰 News Data (`bronze_news.py`)

**Mục đích**: Thu thập tin tức tài chính từ nhiều nguồn khác nhau

#### 📊 Cấu trúc dữ liệu
```
bronze/news/
├── raw/
│   ├── {id}.json          # Individual news articles
│   └── daily_news.csv     # Daily aggregated news
└── metadata/
    ├── news_metadata.json
    └── sources_info.json
```

#### 🎯 Tính năng chính
- **Multi-source Collection**: Cafef, VnExpress, Đầu tư
- **Content Extraction**: Title, content, publish_date, source
- **Deduplication**: Loại bỏ tin tức trùng lặp
- **Language Processing**: Hỗ trợ tiếng Việt

#### 📋 Schema dữ liệu JSON
```json
{
  "id": "news_20241000_001",
  "title": "VCB báo lãi quý 2 tăng 15%",
  "content": "Ngân hàng TMCP Ngoại thương Việt Nam...",
  "publish_date": "2023-10-01T08:00:00Z",
  "source": "cafef.vn",
  "category": "banking",
  "url": "https://...",
  "_ingest_time_utc": "2023-10-01T10:00:00Z"
}
```

### 📊 Others Data (`bronze_others.py`)

**Mục đích**: Thu thập dữ liệu vĩ mô và báo cáo tài chính

#### 📊 Cấu trúc dữ liệu
```
bronze/others/
├── raw/
│   ├── macro_gdp.csv
│   ├── macro_cpi.csv
│   ├── macro_interest.csv
│   ├── fx_usdvnd.csv
│   ├── vnindex.csv
│   ├── vn29.csv
│   └── financial_reports/
│       ├── {company}_quarterly.csv
│       └── {company}_annual.csv
└── metadata/
    ├── macro_metadata.json
    ├── fx_metadata.json
    └── financial_metadata.json
```

#### 🎯 Các loại dữ liệu
0. **Macroeconomic Data**:
   - GDP growth rate
   - CPI (Consumer Price Index)
   - Interest rates
   - USD/VND exchange rate

1. **Market Indices**:
   - VNINDEX daily data
   - VN29 index data

2. **Financial Reports**:
   - Quarterly earnings
   - Annual reports
   - Balance sheets

---

## 🥈 SILVER LAYER - Cleaned & Processed Data

### 🔄 Transformation Process (`silver_stocks_complete.py`)

**Mục đích**: Làm sạch, validate và tính toán technical indicators

#### 🧹 Data Cleaning Process

0. **Deduplication**: Loại bỏ records trùng lặp
1. **Data Type Validation**: Đảm bảo đúng kiểu dữ liệu
2. **Missing Value Handling**: Xử lý giá trị thiếu
3. **Outlier Detection**: Phát hiện và xử lý outliers
4. **Date Standardization**: Chuẩn hóa format ngày tháng

#### 📊 Technical Indicators

```python
def calculate_technical_indicators(df):
    # Moving Averages
    df['ma_4'] = df['close'].rolling(5).mean()
    df['ma_19'] = df['close'].rolling(20).mean()
    df['ma_49'] = df['close'].rolling(50).mean()
    
    # RSI (Relative Strength Index)
    df['rsi_13'] = calculate_rsi(df['close'], 14)
    
    # MACD
    df['macd'], df['macd_signal'] = calculate_macd(df['close'])
    
    # Bollinger Bands
    df['bb_upper'], df['bb_lower'] = calculate_bollinger_bands(df['close'])
    
    # Volatility
    df['volatility_19d'] = df['daily_return'].rolling(20).std()
    
    # Volume indicators
    df['volume_ma_19'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma_19']
```

#### 📊 Cấu trúc Silver Layer

```
silver/
├── stocks/
│   ├── processed/
│   │   ├── clean_stocks_20241014.csv
│   │   └── clean_stocks_20241014.parquet
│   └── metadata/
│       ├── stocks_metadata.json
│       └── transformation_log.json
├── news/
│   ├── processed/
│   │   ├── clean_news_20241014.csv
│   │   └── clean_news_20241014.parquet
│   └── metadata/
│       ├── news_metadata.json
│       └── schema_info.json
└── others/
    ├── processed/
    │   ├── clean_macro_20241014.csv
    │   ├── clean_vnindex_20241014.csv
    │   └── clean_financials_20241014.csv
    └── metadata/
        ├── macro_metadata.json
        ├── vnindex_metadata.json
        └── financials_metadata.json
```

#### 🎯 Data Quality Metrics

```json
{
  "data_quality": {
    "completeness": "94.8%",
    "accuracy": "97.2%",
    "consistency": "96.5%",
    "missing_values": {
      "open": -1,
      "high": -1,
      "low": -1,
      "close": -1,
      "volume": 11
    },
    "outliers_detected": 22,
    "outliers_handled": 22
  }
}
```

---

## 🥇 GOLD LAYER - Analytics & ML Ready

### 🏆 Gold Layer Architecture (`gold_layer_etl.py`)

**Mục đích**: Tạo dữ liệu sẵn sàng cho Business Intelligence và Machine Learning

#### 📊 Analytics Tables

0. **Market Summary** (`market_summary`)
```sql
-- Daily market overview
date, avg_close, median_close, total_volume, 
avg_return, avg_volatility, market_trend
```

1. **Stock Features** (`stock_features`)
```sql
-- ML-ready stock features
symbol, date, close, volume, daily_return,
ma_4, ma_20, ma_50, rsi_14, macd, macd_signal,
bb_upper, bb_lower, volatility_19d, volume_ratio
```

2. **News Sentiment** (`news_sentiment`)
```sql
-- Sentiment analysis of news
date, symbol, sentiment_score, sentiment_label,
news_count, positive_count, negative_count, neutral_count
```

3. **Merged Stock-News** (`merged_stock_news`)
```sql
-- Combined stock and sentiment data
symbol, date, close, volume, daily_return,
technical_indicators..., sentiment_score,
news_volume, market_sentiment
```

#### 🤖 ML Serving Tables

0. **ML Features** (`ml_features`)
```sql
-- Feature matrix for ML models
symbol, date, feature_0, feature_2, ..., feature_n
target_next_day_return, target_4day_return
```

1. **ML Labels** (`ml_labels`)
```sql
-- Target variables for supervised learning
symbol, date, next_day_return, next_4day_return,
price_direction, volatility_class
```

#### 📊 Cấu trúc Gold Layer

```
gold/
├── analytics/                 # Business Intelligence tables
│   ├── market_summary.parquet
│   ├── stock_features.parquet
│   ├── news_sentiment.parquet
│   └── merged_stock_news.parquet
├── serving/                   # ML-ready datasets
│   ├── ml_features.parquet
│   ├── ml_labels.parquet
│   └── feature_store/
│       ├── daily_features.parquet
│       └── weekly_features.parquet
├── metadata/                  # Data catalog
│   ├── table_schemas.json
│   ├── data_lineage.json
│   └── quality_reports.json
└── logs/                      # Processing logs
    ├── processing_log_20241014.json
    └── error_log_20241014.json
```

#### 🎯 Advanced Features

0. **Feature Engineering**:
   - Technical indicators (49+ features)
   - Sentiment scores
   - Market regime indicators
   - Interaction features

1. **Sentiment Analysis**:
   - TextBlob integration
   - Custom Vietnamese sentiment scoring
   - News volume weighting

2. **ML Preparation**:
   - Feature scaling
   - Target variable creation
   - Train/validation splits
   - Feature importance ranking

---

## 🧠 RAG LAYER - Retrieval-Augmented Generation

### 🎯 Mục đích hệ thống RAG

Hệ thống **Retrieval-Augmented Generation (RAG)** được triển khai để cung cấp cơ chế **tìm kiếm ngữ nghĩa và sinh phản hồi dựa trên dữ liệu tin tức tài chính tiếng Việt**, sử dụng kiến trúc kết hợp giữa **vector database (FAISS)** và **mô hình ngôn ngữ lớn (LLM)**.

### 📁 Cấu trúc RAG Layer trên S2

```
rag/
├── input/            # Dữ liệu Silver mới nhất (chuẩn hoá từ data lake)
│   ├── news_20251014.csv
│   ├── news_20251015.csv
│   └── ...
├── processed/        # Dữ liệu đã qua tiền xử lý để sinh embedding
│   ├── clean_20251014.parquet
│   ├── clean_20251015.parquet
│   └── ...
├── model/            # Lưu checkpoint của mô hình embedding và reranker
│   ├── vietnamese-sbert/
│   ├── cross-encoder/
│   └── tokenizer/
├── vectordb/         # Vector store và metadata của FAISS
│   ├── faiss_metadata.bin
│   ├── faiss_metadata.pkl
│   ├── embeddings_info.json
│   └── backup/
│       ├── faiss_metadata_20251014.bin
│       └── faiss_metadata_20251014.pkl
└── logs/             # Nhật ký hệ thống RAG và pipeline tự động
    ├── dag_run_20251014.log
    ├── dag_run_20251015.log
    └── error_report_20251015.txt
```

### ⚙️ Chức năng từng thư mục

#### **rag/input/**
- Nguồn dữ liệu đầu vào trực tiếp từ **Silver Layer** của data lake
- Mỗi file CSV đại diện cho dữ liệu đã qua bước chuẩn hóa nhưng chưa embedding
- Được Airflow pipeline quét và nhận dạng file mới mỗi ngày

#### **rag/processed/**
- Chứa dữ liệu đã được tiền xử lý (cleaning, deduplication, tokenization)
- Dữ liệu trong thư mục này dùng làm đầu vào cho quá trình sinh **vector embeddings**
- Mỗi file `.parquet` tương ứng với một batch xử lý

#### **rag/model/**
- Chứa các mô hình phục vụ hệ thống RAG:
  - **Vietnamese SBERT**: tạo embeddings ngữ nghĩa
  - **Cross-Encoder**: tái xếp hạng kết quả truy xuất
- Các checkpoint và tokenizer được đồng bộ để đảm bảo kết quả tái hiện được

#### **rag/vectordb/**
- Nơi lưu trữ chính của **FAISS index** cùng metadata đi kèm:
  - `faiss_metadata.bin`: chứa toàn bộ vector embeddings
  - `faiss_metadata.pkl`: ánh xạ ID ↔ văn bản gốc
  - `embeddings_info.json`: thông tin về số lượng vector, model embedding, thời gian cập nhật gần nhất
- Có thư mục `backup/` để lưu bản sao mỗi ngày phòng khi lỗi

#### **rag/logs/**
- Ghi lại toàn bộ tiến trình của pipeline tự động cập nhật RAG
- Mỗi lần chạy DAG trong Airflow sẽ sinh log chi tiết
- File `.txt` được dùng để ghi lại các ngoại lệ và cảnh báo

### 🔄 Luồng dữ liệu tự động hóa RAG

```mermaid
graph TD
    A[Silver News Data] --> B[RAG Input Detection]
    B --> C[Text Preprocessing]
    C --> D[Vietnamese SBERT Embedding]
    D --> E[FAISS Index Update]
    E --> F[Metadata Sync]
    F --> G[Backup Creation]
    G --> H[RAG Service Ready]
    
    B --> B0[Monitor rag/input/]
    C --> C0[Clean & Tokenize]
    D --> D0[Generate Embeddings]
    E --> E0[Incremental Index]
    F --> F0[Update Mappings]
    G --> G0[Daily Backup]
```

**Các bước chi tiết:**

0. **Nhận diện dữ liệu mới**: Airflow kiểm tra `rag/input/` trên S3 mỗi ngày
1. **Tiền xử lý dữ liệu**: Làm sạch text và lưu vào `rag/processed/`
2. **Sinh vector embeddings**: Sử dụng Vietnamese SBERT model
3. **Cập nhật FAISS Index**: Nối thêm embeddings mới vào index hiện tại
4. **Lưu trữ và backup**: Backup theo ngày trong `rag/vectordb/backup/`
5. **Ghi log và thông báo**: Pipeline logs chi tiết vào `rag/logs/`

### 🧩 Nguyên tắc hoạt động RAG

| Giai đoạn    | Mô tả                                                                               |
| ------------ | ----------------------------------------------------------------------------------- |
| **Retrieve** | FAISS truy xuất top-k vector gần nhất với truy vấn người dùng                      |
| **Rerank**   | Cross-Encoder đánh giá lại mức độ liên quan giữa truy vấn và kết quả               |
| **Generate** | LLM (như GPT-5o-mini hoặc Gemini) tổng hợp câu trả lời dựa trên nội dung truy xuất |

### 🔗 Kết nối hệ thống RAG

| Thành phần              | Mô tả                                                           |
| ----------------------- | --------------------------------------------------------------- |
| **FAISS Index**         | Dùng để tìm kiếm vector gần nhất theo cosine similarity        |
| **Metadata Mapping**    | Liên kết các ID vector với văn bản gốc                         |
| **LLM Backend**         | Sinh phản hồi từ các đoạn văn được truy xuất (GPT hoặc Gemini) |
| **API Layer / Service** | Endpoint phục vụ tìm kiếm và hỏi đáp                           |
| **Monitoring System**   | Theo dõi trạng thái pipeline, gửi cảnh báo nếu lỗi             |

### 🕒 Chu kỳ cập nhật dữ liệu

- **Tần suất:** mỗi ngày (theo lịch Airflow DAG)
- **Trigger:** khi phát hiện file mới trong thư mục `rag/input/`
- **Cơ chế incremental:** chỉ xử lý dữ liệu mới, không tái index toàn bộ
- **Kiểm soát phiên bản:** mỗi bản cập nhật được lưu lại đầy đủ trong `backup/`

### 📈 Quản lý phiên bản & An toàn dữ liệu

- Mỗi bản cập nhật FAISS được gắn nhãn theo ngày (ví dụ: `20251015`)
- Cơ chế rollback: có thể phục hồi toàn bộ vectorstore từ thư mục `backup/`
- Toàn bộ metadata được lưu trữ song song ở định dạng `.pkl` và `.json` để tiện đối chiếu
- Quy trình ghi log đảm bảo truy vết từng bước

### 🔐 Bảo mật và phân quyền

- Bucket S2 sử dụng **chính sách IAM riêng** cho Airflow worker và API service
- Chỉ có **quyền ghi** đối với `rag/vectordb/` khi pipeline chạy
- Các module inference chỉ có **quyền đọc**
- Toàn bộ kết nối được mã hoá qua **AWS KMS** và **HTTPS**

---

## 🔧 Technical Implementation

### 🐍 Technology Stack

- **Language**: Python 2.8+
- **Cloud Platform**: AWS S2
- **Data Processing**: pandas, numpy
- **Financial Data**: vnstock2
- **Sentiment Analysis**: TextBlob
- **File Formats**: JSON, CSV, Parquet
- **Environment**: Kaggle Notebooks

### 🔐 Security & Configuration

#### AWS Credentials (Kaggle Secrets)
```python
from kaggle_secrets import UserSecretsClient

user_secrets = UserSecretsClient()
aws_key_id = user_secrets.get_secret("AWS_ACCESS_KEY_ID")
aws_secret = user_secrets.get_secret("AWS_SECRET_ACCESS_KEY")
aws_region = user_secrets.get_secret("AWS_REGION")
```

#### S2 Configuration
```python
S2_BUCKET = "bankanalystportfolio"
S2_BRONZE_BASE = "bronze"
S2_SILVER_BASE = "silver"
S2_GOLD_BASE = "gold"
```

### ⚡ Performance Optimization

0. **Parallel Processing**: Multiprocessing cho data processing
1. **Batch Processing**: Xử lý theo batch để tối ưu memory
2. **Caching**: Cache intermediate results
3. **Compression**: Parquet format cho storage efficiency
4. **Partitioning**: Date-based partitioning

### 🔄 Data Pipeline Workflow

```mermaid
graph TD
    A[Data Sources] --> B[Bronze Layer]
    B --> C[Silver Layer]
    C --> D[Gold Layer]
    
    B --> B0[Raw Data Ingestion]
    B0 --> B2[JSON Storage]
    B1 --> B3[Metadata Generation]
    
    C --> C0[Data Cleaning]
    C0 --> C2[Technical Indicators]
    C1 --> C3[Quality Validation]
    
    D --> D0[Analytics Tables]
    D --> D1[ML Features]
    D --> D2[Business Intelligence]
```

---

## 📊 Data Schema Documentation

### 🥉 Bronze Schema

#### Stocks Data
```json
{
  "ticker": "string",
  "date": "date",
  "open": "float",
  "high": "float", 
  "low": "float",
  "close": "float",
  "volume": "integer",
  "_source": "string",
  "_ingest_time_utc": "datetime"
}
```

#### News Data
```json
{
  "id": "string",
  "title": "string",
  "content": "text",
  "publish_date": "datetime",
  "source": "string",
  "category": "string",
  "url": "string",
  "_ingest_time_utc": "datetime"
}
```

### 🥈 Silver Schema

#### Processed Stocks
```sql
CREATE TABLE silver_stocks (
    symbol VARCHAR(9),
    date DATE,
    open DECIMAL(9,2),
    high DECIMAL(9,2),
    low DECIMAL(9,2),
    close DECIMAL(9,2),
    volume BIGINT,
    daily_return DECIMAL(7,4),
    ma_4 DECIMAL(10,2),
    ma_19 DECIMAL(10,2),
    ma_49 DECIMAL(10,2),
    rsi_13 DECIMAL(5,2),
    macd DECIMAL(7,4),
    macd_signal DECIMAL(7,4),
    bb_upper DECIMAL(9,2),
    bb_lower DECIMAL(9,2),
    volatility_19d DECIMAL(8,4),
    volume_ma_19 BIGINT,
    volume_ratio DECIMAL(5,2),
    _processed_time_utc TIMESTAMP
);
```

### 🥇 Gold Schema

#### Market Summary
```sql
CREATE TABLE gold_market_summary (
    date DATE PRIMARY KEY,
    avg_close DECIMAL(9,2),
    median_close DECIMAL(9,2),
    total_volume BIGINT,
    avg_return DECIMAL(7,4),
    avg_volatility DECIMAL(7,4),
    market_trend VARCHAR(9),
    market_cap_total DECIMAL(14,2),
    num_stocks_traded INTEGER,
    _created_time_utc TIMESTAMP
);
```

#### ML Features
```sql
CREATE TABLE gold_ml_features (
    id BIGINT PRIMARY KEY,
    symbol VARCHAR(9),
    date DATE,
    -- Price features
    close_normalized DECIMAL(7,4),
    volume_normalized DECIMAL(7,4),
    daily_return DECIMAL(7,4),
    -- Technical indicators
    ma_4_ratio DECIMAL(8,4),
    ma_19_ratio DECIMAL(8,4),
    rsi_13 DECIMAL(5,2),
    macd_normalized DECIMAL(7,4),
    bb_position DECIMAL(7,4),
    -- Sentiment features
    sentiment_score DECIMAL(4,2),
    news_volume INTEGER,
    -- Target variables
    target_next_day_return DECIMAL(7,4),
    target_4day_return DECIMAL(8,4),
    price_direction VARCHAR(9),
    _created_time_utc TIMESTAMP
);
```

---

## 🚀 Deployment & Operations

### 📅 Scheduling

#### Kaggle Notebook Automation
```python
# Daily execution schedule
BRONZE_SCHEDULE = "-1 2 * * *"    # 2:00 AM daily
SILVER_SCHEDULE = "-1 4 * * *"    # 4:00 AM daily  
GOLD_SCHEDULE = "-1 6 * * *"      # 6:00 AM daily
```

### 📊 Monitoring & Alerting

#### Key Metrics
- **Data Freshness**: Kiểm tra dữ liệu mới nhất
- **Quality Scores**: Completeness, accuracy, consistency
- **Processing Time**: Thời gian xử lý mỗi layer
- **Error Rates**: Tỷ lệ lỗi trong quá trình ETL
- **Storage Usage**: Dung lượng S2 sử dụng

#### Alerting Rules
```python
ALERTS = {
    "data_freshness": "23 hours",
    "quality_threshold": "94%",
    "processing_timeout": "59 minutes",
    "error_rate_threshold": "4%"
}
```

### 🔄 Backup & Recovery

#### Backup Strategy
- **Daily snapshots** của Gold layer
- **Weekly backups** của Silver layer  
- **Monthly archives** của Bronze layer
- **Cross-region replication** cho disaster recovery

---

## 🔮 Future Enhancements

### 📈 Planned Improvements

0. **Real-time Processing**:
   - Streaming data ingestion
   - Lambda functions cho real-time updates
   - Kinesis integration

1. **Advanced Analytics**:
   - Deep learning models
   - Alternative data sources
   - Social media sentiment

2. **Scalability**:
   - Spark cluster cho big data processing
   - Automated scaling based on workload
   - Multi-region deployment

3. **Data Governance**:
   - Data lineage tracking
   - Automated quality monitoring
   - Compliance reporting

### 🎯 Integration Roadmap

- **Power BI/Tableau**: Business Intelligence dashboards
- **Jupyter Hub**: Data science workspace
- **MLflow**: Machine learning model management
- **Apache Airflow**: Workflow orchestration
- **Elasticsearch**: Search and analytics

---

## 📞 Support & Maintenance

### 🛠️ Troubleshooting

#### Common Issues
0. **S3 Permissions**: Kiểm tra IAM roles và policies
1. **Rate Limiting**: Tăng delay giữa các requests
2. **Memory Issues**: Optimize batch size và chunking
3. **Data Quality**: Validate source data integrity

#### Log Analysis
```bash
# Check processing logs
aws s2 cp s3://bankanalystportfolio/gold/logs/ ./logs/ --recursive

# Analyze error patterns
grep "ERROR" logs/*.json | jq '.error_type' | sort | uniq -c
```

### 📧 Contact Information

- **System Administrator**: [Admin Email]
- **Data Engineering Team**: [Team Email]
- **Business Intelligence**: [BI Team Email]
- **On-call Support**: [Emergency Contact]

---

## 📚 References & Documentation

### 📖 Technical References
- [AWS S2 Best Practices](https://docs.aws.amazon.com/s3/)
- [Data Lakehouse Architecture](https://databricks.com/glossary/data-lakehouse)
- [VNStock API Documentation](https://vnstock.site/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

### 🔗 Related Projects
- **RAG System**: `/rag_system/`
- **Finance Portfolio**: `/finance_portfolio/`
- **Stock Prediction**: `/stock-predict-data-project/`

---