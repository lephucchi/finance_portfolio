# 06. Detailed ETL System Architecture

## Overview
Comprehensive documentation of the Finance Portfolio ETL system implementing a modern data lakehouse architecture with Bronze-Silver-Gold layers for Vietnamese banking sector analysis.

**Date**: October 2025  
**Version**: 2.0  
**Author**: Banking Portfolio Team

---

## 🏗️ ETL Architecture

### Data Lakehouse Pattern
Our ETL system follows the medallion architecture pattern:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   SOURCES   │    │   BRONZE    │    │   SILVER    │    │    GOLD     │
│             │───▶│             │───▶│             │───▶│             │
│ Raw Data    │    │ Raw Storage │    │ Cleaned     │    │ Analytics   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Layer Responsibilities

#### Bronze Layer (Raw Data Ingestion)
- **Purpose**: Land raw data from external sources with minimal processing
- **Data Format**: JSON, CSV (as received)
- **Schema**: Schema-on-read, preserve original structure
- **Partitioning**: By date and source type

#### Silver Layer (Data Cleaning & Standardization)
- **Purpose**: Clean, validate, and standardize data
- **Data Format**: Parquet, CSV with consistent schema
- **Schema**: Enforced schema with data quality rules
- **Partitioning**: By date and asset type

#### Gold Layer (Business Intelligence)
- **Purpose**: Aggregated, business-ready datasets
- **Data Format**: Optimized for analytics (Parquet, CSV)
- **Schema**: Star/snowflake schema for dimensional modeling
- **Partitioning**: By business dimensions

---

## 📊 Data Sources & Extraction

### 1. Stock Market Data (VNStock)
```python
# Source: Vietnamese Stock Exchange via vnstock3 library
Data Types:
├── Historical Prices (OHLCV)
├── Trading Volume
├── Market Capitalization
├── Financial Ratios
└── Corporate Actions
```

**Extraction Pattern**:
- **Frequency**: Daily (weekdays only)
- **Tickers**: Top banking stocks (VCB, BID, CTG, etc.)
- **Lookback**: 365 days rolling window
- **API Rate Limiting**: 2 requests/second

### 2. Financial News Data
```python
# Sources: Multiple Vietnamese financial news websites
Data Types:
├── News Articles (Title, Content)
├── Publication Metadata
├── Source Attribution
└── Timestamps
```

**Extraction Pattern**:
- **Frequency**: Real-time scraping
- **Sources**: Multiple financial news portals
- **Language**: Vietnamese (UTF-8 encoding)
- **Content Filtering**: Banking & finance related only

### 3. Economic Indicators
```python
# Sources: Central bank and government statistics
Data Types:
├── Interest Rates
├── Inflation Data
├── GDP Growth
├── Currency Exchange Rates
└── Banking Sector KPIs
```

---

## 🔄 ETL Processing Pipeline

### Bronze Layer Processing

#### Stock Data Extraction
```python
def extract_vnstock_data():
    """
    Extract Vietnamese stock data using vnstock3 library
    
    Process:
    1. Get list of banking tickers
    2. Extract historical data for each ticker
    3. Validate data completeness
    4. Save raw data to S3 bronze layer
    5. Generate extraction metadata
    """
    
    # Key Implementation Details:
    - Error handling for individual ticker failures
    - Retry logic with exponential backoff
    - Data validation (price ranges, volume checks)
    - Metadata tracking for audit trails
```

#### News Data Extraction
```python
def extract_news_data():
    """
    Scrape financial news from Vietnamese sources
    
    Process:
    1. Crawl configured news sources
    2. Extract article content and metadata
    3. Apply content filtering (banking focus)
    4. Save individual articles as JSON files
    5. Track extraction statistics
    """
    
    # Key Implementation Details:
    - Respectful scraping (delays, user-agents)
    - Content deduplication
    - Language detection and encoding handling
    - Source attribution and compliance
```

### Silver Layer Processing

#### Data Cleaning & Standardization
```python
def process_stock_data():
    """
    Clean and standardize stock market data
    
    Transformations:
    1. Data type conversions and validation
    2. Outlier detection and handling
    3. Technical indicator calculations
    4. Schema standardization
    5. Quality scoring
    """
    
    # Technical Indicators Calculated:
    - Simple Moving Averages (SMA 10, 20)
    - Exponential Moving Averages (EMA 12, 26)
    - MACD (Moving Average Convergence Divergence)
    - RSI (Relative Strength Index)
    - Bollinger Bands
    - Daily Returns and Volatility
```

#### Sentiment Analysis
```python
def process_news_data():
    """
    Apply NLP processing to news content
    
    Transformations:
    1. Text cleaning and normalization
    2. Vietnamese sentiment analysis
    3. Topic categorization
    4. Content quality scoring
    5. Entity extraction (banking keywords)
    """
    
    # NLP Pipeline:
    - Text preprocessing (remove HTML, special chars)
    - Vietnamese keyword-based sentiment scoring
    - Banking sector topic classification
    - Content length and quality metrics
```

### Gold Layer Processing

#### Analytics & ML Features
```python
def create_analytics_tables():
    """
    Generate business intelligence datasets
    
    Outputs:
    1. Market summary dashboards
    2. Sentiment analytics
    3. ML-ready feature sets
    4. Risk assessment metrics
    """
    
    # Business Intelligence Features:
    - Daily market summaries by bank tier
    - Sentiment trend analysis
    - Technical signal aggregations
    - Performance rankings and comparisons
```

---

## 📁 Data Storage Structure

### S3 Bucket Organization
```
bankanalystportfolio/
├── bronze/                     # Raw data layer
│   ├── stocks/
│   │   ├── raw/               # Raw stock data files
│   │   └── metadata/          # Extraction metadata
│   ├── news/
│   │   ├── raw/               # Individual news articles
│   │   └── metadata/          # Scraping metadata
│   └── others/
│       ├── raw/               # Economic indicators
│       └── metadata/          # Collection metadata
├── silver/                     # Cleaned data layer
│   ├── stocks/
│   │   ├── processed/         # Cleaned stock data
│   │   └── metadata/          # Transformation metadata
│   └── news/
│       ├── processed/         # Processed news with sentiment
│       └── metadata/          # Processing metadata
└── gold/                      # Analytics layer
    ├── analytics/
    │   ├── sentiment_analysis/ # News sentiment insights
    │   ├── market_summary/     # Daily market reports
    │   └── metadata/          # Analytics metadata
    └── serving/
        ├── ml_features/       # ML-ready datasets
        └── metadata/          # Feature engineering metadata
```

### File Naming Conventions
```python
# Bronze Layer
bronze/stocks/raw/stocks_YYYYMMDD.json
bronze/news/raw/article_{uuid}.json

# Silver Layer  
silver/stocks/processed/clean_stocks_YYYYMMDD.csv
silver/news/processed/clean_news_YYYYMMDD.json

# Gold Layer
gold/analytics/market_summary/summary_YYYYMMDD.json
gold/serving/ml_features/ml_features_YYYYMMDD.csv
```

---

## ⚙️ Technical Implementation

### Apache Airflow Orchestration
```python
# DAG Structure
bronze_layer_pipeline → silver_layer_pipeline → gold_layer_pipeline
                                              ↘
                                               rag_pipeline
```

#### DAG Configuration
- **Schedule**: Daily at 6:00 AM (after market close)
- **Catchup**: Disabled (only process current date)
- **Max Active Runs**: 1 (prevent parallel execution)
- **Retry Policy**: 2 retries with 5-minute delay
- **Timeout**: 2 hours per DAG

#### Task Dependencies
```python
# Bronze Layer Tasks
start_bronze → [extract_stocks, extract_news, extract_others] → validate_bronze → end_bronze

# Silver Layer Tasks  
start_silver → [process_stocks, process_news] → validate_silver → end_silver

# Gold Layer Tasks
start_gold → [create_analytics, create_ml_features] → validate_gold → end_gold
```

### Data Quality Framework

#### Validation Rules
```python
Stock Data Quality Checks:
✓ Price ranges within reasonable bounds
✓ Volume > 0 for trading days
✓ No missing OHLC values
✓ Date consistency and ordering
✓ Ticker symbol validation

News Data Quality Checks:
✓ Content length > minimum threshold
✓ Valid publication dates
✓ Source attribution present
✓ Language detection (Vietnamese)
✓ Duplicate content detection
```

#### Error Handling Strategy
1. **Graceful Degradation**: Continue processing other assets if one fails
2. **Retry Logic**: Exponential backoff for transient failures
3. **Data Quarantine**: Isolate invalid records for manual review
4. **Alert System**: Notifications for critical failures
5. **Rollback Capability**: Ability to reprocess specific dates

---

## 🔧 Configuration Management

### Environment Variables
```bash
# S3 Configuration
S3_BUCKET=bankanalystportfolio
AWS_REGION=ap-southeast-1

# API Configuration  
VNSTOCK_RATE_LIMIT=2
NEWS_SCRAPING_DELAY=1

# Processing Configuration
MAX_RETRY_ATTEMPTS=3
BATCH_SIZE=50
LOOKBACK_DAYS=365
```

### Pipeline Parameters
```python
# Bronze Layer Configuration
BANKING_TICKERS = ["VCB", "BID", "CTG", "AGR", "VPB", "TCB", "MBB"]
NEWS_SOURCES = ["cafef.vn", "vnexpress.net/kinh-doanh", "dantri.com.vn/kinh-doanh"]

# Silver Layer Configuration
TECHNICAL_INDICATORS = {
    "SMA_PERIODS": [10, 20],
    "EMA_PERIODS": [12, 26],
    "RSI_PERIOD": 14,
    "BOLLINGER_PERIOD": 20
}

# Gold Layer Configuration
ANALYTICS_TIMEFRAMES = ["1D", "7D", "30D", "90D"]
ML_FEATURE_WINDOW = 30  # days
```

---

## 📈 Performance Optimization

### Processing Optimizations
1. **Parallel Processing**: Multiple workers for independent tasks
2. **Batch Operations**: Process multiple records together
3. **Caching**: Cache frequently accessed reference data
4. **Compression**: Use efficient storage formats (Parquet)
5. **Partitioning**: Optimize data layout for query performance

### Resource Management
```python
# Airflow Resource Allocation
Default Pool: 16 slots
Bronze Tasks: 4 slots each
Silver Tasks: 6 slots each  
Gold Tasks: 8 slots each

# Memory Management
Pandas Chunk Size: 10,000 rows
S3 Multipart Upload: 8MB chunks
Connection Pooling: 10 connections max
```

---

## 🚀 Deployment & Operations

### Container Infrastructure
```yaml
# Docker Compose Services
services:
  airflow-webserver:
    resources:
      limits:
        memory: 2G
        cpus: 1.0
        
  airflow-scheduler:
    resources:
      limits:
        memory: 4G
        cpus: 2.0
```

### Monitoring & Alerting
1. **Pipeline Health**: DAG success/failure rates
2. **Data Quality**: Record counts and validation metrics
3. **Performance**: Processing times and resource usage
4. **Business Metrics**: Data freshness and completeness

### Backup & Recovery
- **S3 Versioning**: Automatic backup of all data files
- **Metadata Snapshots**: Daily exports of pipeline metadata
- **Configuration Backup**: Git-based version control
- **Recovery Procedures**: Documented rollback processes

---

## 📋 Data Governance

### Data Lineage
Every data transformation is tracked with complete lineage information:
```json
{
  "data_lineage": "bronze/stocks/raw/stocks_20251017.json -> silver/stocks/processed/clean_stocks_20251017.csv",
  "transformations_applied": ["data_cleaning", "technical_indicators", "quality_validation"],
  "source_record_count": 1250,
  "target_record_count": 1247,
  "transformation_timestamp": "2025-10-17T04:30:00Z"
}
```

### Compliance & Security
- **Data Privacy**: No personal information collected
- **Access Control**: IAM-based permissions for S3 access
- **Audit Trails**: Complete logging of all data operations
- **Retention Policy**: 2-year retention for raw data, 5-year for processed

### Quality Assurance
- **Automated Testing**: Unit tests for all transformation functions
- **Data Validation**: Comprehensive checks at each layer
- **Manual Review**: Weekly data quality reports
- **Continuous Improvement**: Monthly pipeline optimization reviews

---

## 🔍 Troubleshooting Guide

### Common Issues & Solutions

#### 1. VNStock API Rate Limiting
```python
# Problem: Too many requests to vnstock API
# Solution: Implement exponential backoff
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

#### 2. News Scraping Failures
```python
# Problem: Website blocking or content changes
# Solution: Robust error handling and alternative sources
def scrape_with_fallback(primary_source, fallback_sources):
    try:
        return scrape_source(primary_source)
    except Exception as e:
        logger.warning(f"Primary source failed: {e}")
        for fallback in fallback_sources:
            try:
                return scrape_source(fallback)
            except Exception:
                continue
        raise Exception("All sources failed")
```

#### 3. S3 Upload Timeouts
```python
# Problem: Large files timing out during upload
# Solution: Multipart upload with retries
from boto3.s3.transfer import TransferConfig

config = TransferConfig(
    multipart_threshold=1024 * 25,  # 25MB
    max_concurrency=10,
    multipart_chunksize=1024 * 25,
    use_threads=True
)
```

---

## 📊 Success Metrics

### Pipeline KPIs
- **Data Freshness**: < 4 hours from market close
- **Data Completeness**: > 95% of expected records
- **Pipeline Success Rate**: > 98% successful runs
- **Processing Time**: < 60 minutes end-to-end
- **Data Quality Score**: > 90% passing all validations

### Business Value Metrics
- **Market Coverage**: 15+ banking stocks tracked
- **News Coverage**: 500+ articles processed daily
- **Analytics Latency**: Real-time insights available
- **ML Model Performance**: 75%+ prediction accuracy
- **User Satisfaction**: Measured through dashboard usage

---

*This ETL system provides a robust, scalable foundation for Vietnamese banking sector analysis with comprehensive data quality, monitoring, and governance capabilities.*