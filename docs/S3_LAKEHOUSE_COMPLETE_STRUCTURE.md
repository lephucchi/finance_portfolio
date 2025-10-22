# 📦 S3 LAKEHOUSE STRUCTURE - COMPLETE REFERENCE

## 📋 Table of Contents
1. [Overall Architecture](#overall-architecture)
2. [Bronze Layer](#bronze-layer)
3. [Silver Layer](#silver-layer)
4. [Gold Layer](#gold-layer)
5. [Metadata Files](#metadata-files)
6. [Query Examples](#query-examples)

---

## Overall Architecture

```
s3://bankanalystportfolio/
├── bronze/                          # RAW DATA LAYER
│   ├── stocks/raw/
│   ├── news/raw/
│   └── macro/raw/
│
├── silver/                          # CLEANED & STANDARDIZED
│   ├── stocks/
│   ├── news/
│   └── macro/
│
├── gold/                            # ANALYTICS & FEATURES
│   ├── analytics/
│   │   ├── macro_indicators/
│   │   ├── market_features/
│   │   ├── news_summary/
│   │   └── sector_performance/
│   │
│   ├── sentiment_analysis/
│   │
│   ├── metadata/                    # Partition metadata & lineage
│   │
│   └── serving/                     # Ready-to-use for BI/ML
│
└── athena_results/                  # QUERY RESULTS (Athena)
```

### Hive-style Partitioning Strategy

Tất cả dữ liệu được partition theo **ngày xử lý**:
```
partition_date=YYYY-MM-DD/
```

**Lợi ích:**
- ✅ Athena tự động discover partitions
- ✅ Query optimization (partition pruning)
- ✅ Incremental processing (daily updates)
- ✅ Data retention policies (delete old partitions)

---

## BRONZE LAYER

### 📊 Purpose
- Lưu trữ dữ liệu **RAW** từ các nguồn khác nhau
- Không có xử lý hay cleaning
- Format: JSON (news, stocks), CSV (macro)
- Tập trung vào **collection** không phải transformation

---

### 1️⃣ Bronze - Stocks

**Path:** `s3://bankanalystportfolio/bronze/stocks/raw/`

**Collected by:** `bronze_stocks.py`

**Structure:**
```
bronze/stocks/raw/
├── ACB_2025-10-18.json
├── ACB_2025-10-17.json
├── VCB_2025-10-18.json
├── VCB_2025-10-17.json
└── ... (150,000+ files)
```

**File Format:** JSON (1 stock OHLCV per file)

**Sample JSON Structure:**
```json
{
  "symbol": "ACB",
  "data_date": "2025-10-18",
  "open": 25300.0,
  "high": 25500.0,
  "low": 25100.0,
  "close": 25400.0,
  "volume": 5234000,
  "price_change": 100.0,
  "price_change_pct": 0.39,
  "_source": "bronze_stocks.py",
  "_ingest_time": "2025-10-18T07:00:00.000000+00:00"
}
```

**Key Columns:**
| Column | Type | Description |
|--------|------|-------------|
| symbol | string | Stock ticker (ACB, VCB, etc.) |
| data_date | string | Trading date (YYYY-MM-DD) |
| open | float | Opening price |
| high | float | Highest price |
| low | float | Lowest price |
| close | float | Closing price |
| volume | integer | Trading volume |
| price_change | float | Absolute price change |
| price_change_pct | float | Percentage change |
| _source | string | Data source identifier |
| _ingest_time | string | Ingestion timestamp (ISO8601) |

**Partitioning:** ❌ NOT PARTITIONED (Raw collection only)

---

### 2️⃣ Bronze - News

**Path:** `s3://bankanalystportfolio/bronze/news/raw/`

**Collected by:** `bronze_news.py`

**Structure:**
```
bronze/news/raw/
├── uuid_1.json
├── uuid_2.json
├── uuid_3.json
└── ... (8,439 files)
```

**File Format:** JSON (1 news article per file)

**Sample JSON Structure:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2025-10-13 02:17:51.668538",
  "source": "google_cse",
  "title": "Thị trường chứng khoán Việt Nam tăng mạnh",
  "combined_text": "VNINDEX tăng 1.5% trong phiên giao dịch hôm nay...",
  "sentiment_score": 0.75,
  "link": "https://example.com/article",
  "_source": "bronze_news.py",
  "_ingest_time": "2025-10-18T09:30:00.000000+00:00"
}
```

**Key Columns:**
| Column | Type | Description |
|--------|------|-------------|
| id | string | Unique identifier (UUID) |
| date | string | Article date (multiple formats support) |
| source | string | News source (google_cse, etc.) |
| title | string | Article title |
| combined_text | string | Full article content |
| sentiment_score | float | Sentiment score (-1 to 1) |
| link | string | Article URL |
| _source | string | Data source identifier |
| _ingest_time | string | Ingestion timestamp (ISO8601) |

**Date Formats Handled:**
- `2025-10-13 02:17:51.668538` (full timestamp)
- `2025-10-17` (date only)
- `2025-10-13T02:17:51.168680+00:00` (ISO8601)
- `2025-10-13 02:17:51` (datetime)

**Partitioning:** ❌ NOT PARTITIONED (Raw collection only)

---

### 3️⃣ Bronze - Macro (Economic Indicators)

**Path:** `s3://bankanalystportfolio/bronze/macro/raw/`

**Collected by:** `bronze_macro.py`

**Structure:**
```
bronze/macro/raw/
├── gdp.csv
├── cpi.csv
├── inflation.csv
├── interest_rate.csv
├── unemployment.csv
├── credit_growth.csv
├── deposit_growth.csv
├── forex/
│   ├── usd_vnd.csv
│   ├── eur_vnd.csv
│   ├── jpy_vnd.csv
│   ├── gbp_vnd.csv
│   └── cny_vnd.csv
├── indices/
│   ├── vnindex.csv
│   ├── vn30.csv
│   ├── vn100.csv
│   └── upcom.csv
├── sectors/
│   ├── banking.csv
│   ├── securities.csv
│   ├── insurance.csv
│   ├── real_estate.csv
│   ├── energy.csv
│   ├── materials.csv
│   ├── industrials.csv
│   ├── consumer_discretionary.csv
│   ├── consumer_staples.csv
│   ├── healthcare.csv
│   ├── technology.csv
│   └── utilities.csv
├── banking/
│   ├── capital_adequacy.csv
│   ├── npl_ratio.csv
│   ├── loan_deposit_ratio.csv
│   └── ...
└── real_estate/
    ├── construction_index.csv
    ├── real_estate_price_index.csv
    ├── residential_demand.csv
    └── ...
```

**File Format:** CSV

**Sample CSV Structure (GDP.csv):**
```csv
date,value
2025-10-18,312453.50
2025-10-17,312120.30
2025-10-16,311850.75
...
```

**Sample CSV Structure (banking.csv):**
```csv
date,credit_growth,deposit_growth,npl_ratio
2025-10-18,5.2,4.1,0.85
2025-10-17,5.1,4.0,0.86
2025-10-16,5.0,3.9,0.87
...
```

**Macro Data Categories:**

| Category | Files | Description |
|----------|-------|-------------|
| **Economic** | GDP, CPI, Inflation, Interest Rate, Unemployment | Macro indicators |
| **FX Data** | USD/VND, EUR/VND, JPY/VND, GBP/VND, CNY/VND | Exchange rates |
| **Indices** | VNINDEX, VN30, VN100, UPCOM | Stock indices |
| **Sectors** | 12 sector files | Sector performance |
| **Banking** | 5 banking indicators | Credit, NPL, ratios |
| **Real Estate** | 5 real estate indicators | Construction, prices |

**Total:** 50+ CSV files

**Partitioning:** ❌ NOT PARTITIONED (Raw collection only)

---

## SILVER LAYER

### 📊 Purpose
- **CLEANED & STANDARDIZED** data từ Bronze
- Unified schema cho mỗi data type
- Ready for analytics (Gold layer)
- Partition by date: `partition_date=YYYY-MM-DD`

---

### 1️⃣ Silver - News

**Path:** `s3://bankanalystportfolio/silver/news/partition_date=YYYY-MM-DD/`

**Created by:** `bronze_to_silver_macro_news.py` (News processing)

**Partitioning:** `partition_date=YYYY-MM-DD`

**Example:**
```
silver/news/
├── partition_date=2025-10-18/
│   ├── news_cleaned.parquet
│   └── _metadata.json
├── partition_date=2025-10-17/
│   ├── news_cleaned.parquet
│   └── _metadata.json
└── partition_date=2025-10-16/
    ├── news_cleaned.parquet
    └── _metadata.json
```

**File Format:** Parquet (Snappy compression)

**Schema:**
```
root
├── id: string (unique identifier)
├── data_date: date (article date, YYYY-MM-DD)
├── source: string (news source)
├── title: string (article title)
├── content: string (full text)
├── sentiment_score: double (sentiment, -1 to 1)
├── _source: string (data source: "google_cse")
└── _ingest_time: string (ISO8601 timestamp)
```

**Sample Data (Parquet):**
```
id                                  | data_date  | source     | title                           | sentiment_score
550e8400-e29b-41d4-a716-446655440000 | 2025-10-18 | google_cse | VNINDEX tăng 1.5% hôm nay      | 0.75
550e8400-e29b-41d4-a716-446655440001 | 2025-10-18 | google_cse | Thị trường điều chỉnh giảm sâu | -0.45
550e8400-e29b-41d4-a716-446655440002 | 2025-10-17 | google_cse | Cổ phiếu ngân hàng lên kịch trần| 0.82
```

**Metadata File (_metadata.json):**
```json
{
  "table_name": "silver_news",
  "partition_date": "2025-10-18",
  "row_count": 4523,
  "columns": ["id", "data_date", "source", "title", "content", "sentiment_score", "_source", "_ingest_time"],
  "batch_processing": {
    "batch_size": 500,
    "total_batches": 17,
    "total_files_processed": 8439
  },
  "processing_timestamp": "2025-10-18T10:45:23.123456+00:00"
}
```

**Statistics:**
- **Row count per partition:** 4,000 - 5,000 records
- **File size:** ~20-30 MB per partition
- **Deduplication:** Applied (removed duplicates from Bronze)

---

### 2️⃣ Silver - Macro

**Path:** `s3://bankanalystportfolio/silver/macro/partition_date=YYYY-MM-DD/`

**Created by:** `bronze_to_silver_macro_news.py` (Macro processing)

**Partitioning:** `partition_date=YYYY-MM-DD`

**Example:**
```
silver/macro/
├── partition_date=2025-10-18/
│   ├── macro_data.parquet
│   └── _metadata.json
├── partition_date=2025-10-17/
│   ├── macro_data.parquet
│   └── _metadata.json
└── partition_date=2025-10-16/
    ├── macro_data.parquet
    └── _metadata.json
```

**File Format:** Parquet (Snappy compression)

**Schema:**
```
root
├── data_date: date (measurement date, YYYY-MM-DD)
├── indicator_name: string (GDP, CPI, USD/VND, VNINDEX, etc.)
├── indicator_value: double (numeric value)
├── _source: string (source filename: "gdp.csv", "usd_vnd.csv")
└── _ingest_time: string (ISO8601 timestamp)
```

**Sample Data (Parquet):**
```
data_date  | indicator_name      | indicator_value | _source
2025-10-18 | Gdp                 | 312453.50       | gdp.csv
2025-10-18 | Cpi                 | 112.35          | CPI.csv
2025-10-18 | Inflation           | 3.45            | inflation.csv
2025-10-18 | Interest Rate       | 5.50            | interest_rate.csv
2025-10-18 | Unemployment        | 2.15            | unemployment.csv
2025-10-18 | Usd Vnd             | 24580.00        | usd_vnd.csv
2025-10-18 | Eur Vnd             | 26750.00        | eur_vnd.csv
2025-10-18 | Vnindex             | 1245.50         | vnindex.csv
2025-10-18 | Banking             | 87.30           | banking.csv
2025-10-17 | Gdp                 | 312120.30       | gdp.csv
```

**Metadata File (_metadata.json):**
```json
{
  "table_name": "silver_macro",
  "partition_date": "2025-10-18",
  "row_count": 1250,
  "columns": ["data_date", "indicator_name", "indicator_value", "_source", "_ingest_time"],
  "batch_processing": {
    "batch_size": 500,
    "total_batches": 2,
    "total_files_processed": 50
  },
  "processing_timestamp": "2025-10-18T10:50:15.654321+00:00"
}
```

**Statistics:**
- **Row count per partition:** 1,000 - 1,500 records
- **File size:** ~5-10 MB per partition
- **Indicators:** 50+ different macro indicators

---

### 3️⃣ Silver - Stocks

**Path:** `s3://bankanalystportfolio/silver/stocks/partition_date=YYYY-MM-DD/`

**Created by:** `bronze_to_silver_v6.py` (Stocks processing)

**Partitioning:** `partition_date=YYYY-MM-DD`

**Example:**
```
silver/stocks/
├── partition_date=2025-10-18/
│   ├── stock_data.parquet
│   └── _metadata.json
├── partition_date=2025-10-17/
│   ├── stock_data.parquet
│   └── _metadata.json
└── partition_date=2025-10-16/
    ├── stock_data.parquet
    └── _metadata.json
```

**File Format:** Parquet (Snappy compression)

**Schema:**
```
root
├── symbol: string (stock ticker: ACB, VCB, etc.)
├── data_date: date (trading date, YYYY-MM-DD)
├── open: double (opening price)
├── high: double (highest price)
├── low: double (lowest price)
├── close: double (closing price)
├── volume: long (trading volume)
├── price_change: double (absolute change)
├── price_change_pct: double (percentage change)
├── _source: string (data source: "bronze_stocks.py")
└── _ingest_time: string (ISO8601 timestamp)
```

**Sample Data (Parquet):**
```
symbol | data_date  | open    | high    | low     | close   | volume
ACB    | 2025-10-18 | 25300.0 | 25500.0 | 25100.0 | 25400.0 | 5234000
VCB    | 2025-10-18 | 92500.0 | 93000.0 | 92000.0 | 92800.0 | 3421000
BID    | 2025-10-18 | 37200.0 | 37500.0 | 37000.0 | 37400.0 | 2156000
TCB    | 2025-10-18 | 18500.0 | 18700.0 | 18300.0 | 18600.0 | 4523000
CTG    | 2025-10-18 | 32100.0 | 32400.0 | 31900.0 | 32200.0 | 6234000
```

**Statistics:**
- **Row count per partition:** 2,000 - 3,000 stocks per day
- **File size:** ~30-50 MB per partition
- **Symbols:** 700+ listed stocks

---

## GOLD LAYER - 4 LAYER ARCHITECTURE (OPTION 2 - RECOMMENDED)

### 📊 Overall Structure

```
s3://bankanalystportfolio/gold/
│
├── 🔷 analytics/                       # LAYER 1: Business Tables (Athena queryable)
│   ├── market_features/
│   ├── sector_performance/
│   ├── news_summary/
│   └── macro_indicators/
│
├── 🔶 sentiment_analysis/              # LAYER 2: Specialized Sentiment (Athena queryable)
│   └── (sentiment data partitioned by date)
│
├── 🟡 serving/                         # LAYER 3: Pre-aggregated Cache (BI/Dashboard layer)
│   ├── market_dashboard/               # Fast loads for Tableau/PowerBI
│   ├── sentiment_features/             # ML-ready features
│   ├── macro_features/                 # Forecasting data
│   └── risk_metrics/                   # Risk analysis
│
└── ⚪ metadata/                         # LAYER 4: System Metadata (NOT in Athena)
    ├── pipeline_runs/                  # Execution history
    └── quality_metrics/                # Data quality tracking
```

### 🎯 Design Principles

| Layer | Purpose | Query Engine | Use Case | Speed |
|-------|---------|--------------|----------|-------|
| **analytics/** | Detailed business tables | ✅ Athena SQL | Ad-hoc queries, reports | Medium (1-30s) |
| **sentiment_analysis/** | Specialized sentiment | ✅ Athena SQL | Sentiment trends, analysis | Medium (1-30s) |
| **serving/** | Pre-aggregated cache | ❌ S3 direct | Dashboard display, fast loads | Fast (< 100ms) |
| **metadata/** | System tracking | ❌ Manual/API | Lineage, quality, debugging | N/A |

---

## LAYER 1: 🔷 ANALYTICS (Athena Queryable)

### Purpose
- **Detailed business tables** for analytics
- Partitioned by date for incremental processing
- Ready for Athena queries
- Used for: reports, ad-hoc analysis, ML training

### 1️⃣ Analytics - Market Features (Stocks)

**Path:** `s3://bankanalystportfolio/gold/analytics/market_features/partition_date=YYYY-MM-DD/`

**Created by:** `silver_to_gold.py` (v2.0-option2)

**Schema:**
```
root
├── symbol: string
├── data_date: date
├── open: double
├── high: double
├── low: double
├── close: double
├── volume: long
├── price_change_pct: double
├── MA_5: double
├── MA_10: double
├── MA_20: double
├── MA_30: double
├── RSI_14: double
├── volatility_7d: double
├── price_change_5d: double
└── price_change_10d: double
```

**Sample Data:**
```
symbol | data_date  | open   | close  | MA_20  | RSI_14 | volatility_7d
ACB    | 2025-10-18 | 25300  | 25400  | 25320  | 65.2   | 1.8
VCB    | 2025-10-18 | 28500  | 28600  | 28450  | 68.5   | 1.5
```

**Use Cases:**
- 📊 Technical analysis
- 💹 Trend detection
- 📈 Volatility analysis
- 🎯 Trading signal generation

---

### 2️⃣ Analytics - Sector Performance (Stocks)

**Path:** `s3://bankanalystportfolio/gold/analytics/sector_performance/partition_date=YYYY-MM-DD/`

**Schema:**
```
root
├── data_date: date
├── sector: string
├── avg_price_change_pct: double
├── avg_volatility: double
└── avg_volume: double
```

**Use Cases:**
- 📊 Sector rotation
- 💰 Portfolio allocation
- 📈 Risk assessment

---

### 3️⃣ Analytics - News Summary (News)

**Path:** `s3://bankanalystportfolio/gold/analytics/news_summary/partition_date=YYYY-MM-DD/`

**Schema:**
```
root
├── data_date: date
├── total_articles: long
├── unique_sources: long
├── avg_sentiment: double
├── articles_positive: long
├── articles_negative: long
├── avg_title_length: double
└── top_source: string
```

**Use Cases:**
- 📊 News volume trends
- 📈 Media coverage analysis
- 🔝 Source comparison

---

### 4️⃣ Analytics - Macro Indicators (Macro)

**Path:** `s3://bankanalystportfolio/gold/analytics/macro_indicators/partition_date=YYYY-MM-DD/`

**Schema:**
```
root
├── data_date: date
├── indicator_name: string
├── indicator_value: double
├── MA_7: double
├── MA_30: double
├── value_change: double
├── value_change_pct: double
└── indicator_source: string
```

**Sample Data:**
```
data_date  | indicator_name | indicator_value | MA_7      | MA_30     
2025-10-18 | Gdp            | 312453.50       | 312200.14 | 311800.25
2025-10-18 | Inflation      | 3.45            | 3.42      | 3.40
2025-10-18 | Usd Vnd        | 24580.00        | 24560.29  | 24500.00
```

**Use Cases:**
- 📊 Macro trend analysis
- � FX forecasting
- 📈 Economic tracking

---

## LAYER 2: � SENTIMENT ANALYSIS (Athena Queryable)

### Purpose
- **Specialized sentiment layer** focusing on news sentiment
- Aggregated by date and source
- Ready for Athena queries
- Used for: sentiment trends, news analysis, sentiment-based trading

### Sentiment Analysis Table

**Path:** `s3://bankanalystportfolio/gold/sentiment_analysis/partition_date=YYYY-MM-DD/`

**Schema:**
```
root
├── data_date: date
├── source: string
├── article_count: long
├── avg_sentiment: double (-1 to 1)
├── positive_count: long
├── negative_count: long
├── neutral_count: long
└── sentiment_change_pct: double
```

**Sample Data:**
```
data_date  | source     | article_count | avg_sentiment | positive_count | negative_count
2025-10-18 | google_cse | 245           | 0.52          | 156            | 45
2025-10-18 | vnexpress  | 180           | 0.38          | 98             | 32
```

**Use Cases:**
- 📰 Sentiment analysis
- 💬 Market psychology
- 🎯 Sentiment signals
- 📊 Investor mood tracking

---

## LAYER 3: 🟡 SERVING (Cache Layer for BI/Dashboard)

### Purpose
- **Pre-aggregated data** for fast dashboard loads
- Optimized for consumption (not for ad-hoc queries)
- Does NOT use Athena (direct S3 read or cache)
- Used for: BI dashboards, real-time displays, fast API responses

### Why Separate Serving Layer?

```
Dashboard Load Time Comparison:

❌ Without serving layer:
   Dashboard → Athena Query → S3 → Process → Display (5-30 seconds)

✅ With serving layer:
   Dashboard → Serving Cache → Display (< 100ms)
   (Athena feeds cache periodically)
```

### 1️⃣ Serving - Market Dashboard

**Path:** `s3://bankanalystportfolio/gold/serving/market_dashboard/partition_date=YYYY-MM-DD/`

**Schema:**
```
root
├── symbol: string
├── data_date: date
├── open: double
├── close: double
├── volume: long
├── MA_20: double
├── RSI_14: double
├── volatility_7d: double
└── price_change_pct: double
```

**Use:** Tableau, PowerBI, Grafana dashboards

**Benefits:**
- ✅ Subset of market_features (only dashboard columns)
- ✅ Pre-calculated aggregations
- ✅ Fast S3 reads (< 100ms)

---

### 2️⃣ Serving - Sentiment Features

**Path:** `s3://bankanalystportfolio/gold/serving/sentiment_features/partition_date=YYYY-MM-DD/`

**Schema:**
```
root
├── data_date: date
├── source: string
├── article_count: long
├── avg_sentiment: double
├── positive_pct: double
└── negative_pct: double
```

**Use:** ML models, sentiment dashboards

**Benefits:**
- ✅ Pre-calculated percentages (save compute)
- ✅ Feature-ready for ML
- ✅ Fast inference

---

### 3️⃣ Serving - Macro Features

**Path:** `s3://bankanalystportfolio/gold/serving/macro_features/partition_date=YYYY-MM-DD/`

**Schema:**
```
root
├── data_date: date
├── indicator_name: string
├── indicator_value: double
├── MA_7: double
├── MA_30: double
└── value_change_pct: double
```

**Use:** Macro forecasting, economic dashboards

---

### 4️⃣ Serving - Risk Metrics

**Path:** `s3://bankanalystportfolio/gold/serving/risk_metrics/partition_date=YYYY-MM-DD/`

**Schema:**
```
root
├── data_date: date
├── symbol: string
└── volatility_7d: double
```

**Use:** Risk dashboards, portfolio analysis

---

## LAYER 4: ⚪ METADATA (System Layer - NOT in Athena)

### Purpose
- **Track data lineage** and transformations
- **Monitor data quality** and SLAs
- **Audit trail** for compliance
- NOT queryable via Athena (internal system use)

### Pipeline Runs

**Path:** `s3://bankanalystportfolio/gold/metadata/pipeline_runs/{partition_date}/run_metadata.json`

```json
{
  "pipeline_run_id": "gold_transform_2025-10-18_1729257600",
  "timestamp": "2025-10-18T18:00:00Z",
  "partition_date": "2025-10-18",
  "duration_seconds": 245,
  "status": "SUCCESS",
  "tables_created": {
    "market_features": true,
    "sentiment_analysis": true,
    "macro_indicators": true,
    "sector_performance": true,
    "news_summary": true
  },
  "version": "v2.0-option2"
}
```

**Use Cases:**
- ✅ Pipeline monitoring
- ✅ Performance tracking
- ✅ Audit logs
- ✅ SLA validation

---

### Quality Metrics

**Path:** `s3://bankanalystportfolio/gold/metadata/quality_metrics/{partition_date}/metrics.json`

```json
{
  "partition_date": "2025-10-18",
  "timestamp": "2025-10-18T18:10:00Z",
  "table_metrics": {
    "market_features": {
      "row_count": 3000,
      "null_count": 12,
      "columns": 15
    },
    "sentiment_analysis": {
      "row_count": 500,
      "null_count": 0,
      "columns": 8
    }
  }
}
```

**Use Cases:**
- ✅ Data quality monitoring
- ✅ Anomaly detection
- ✅ Data validation
- ✅ Alert triggers

---

## 📊 Gold Layer Statistics (Option 2)

| Layer | Table | Rows/Day | Size/Day | Athena |
|-------|-------|----------|----------|--------|
| **analytics/** | market_features | 3,000 | 35 MB | ✅ |
| | sector_performance | 12 | < 1 MB | ✅ |
| | news_summary | 1 | < 1 MB | ✅ |
| | macro_indicators | 1,200 | 8 MB | ✅ |
| **sentiment_analysis/** | sentiment_daily | 500 | 5 MB | ✅ |
| **serving/** | market_dashboard | 3,000 | 25 MB | ❌ |
| | sentiment_features | 500 | 4 MB | ❌ |
| | macro_features | 1,200 | 6 MB | ❌ |
| | risk_metrics | 3,000 | 15 MB | ❌ |
| **metadata/** | pipeline_runs | 1 | < 1 KB | ❌ |
| | quality_metrics | 1 | < 1 KB | ❌ |
| **TOTAL** | | | **~99 MB** | 5 tables |

---

## � Governance & Access Control

```
Typical User Permissions:

Data Analysts:
✅ Query analytics/* (Athena)
✅ Query sentiment_analysis/* (Athena)
❌ Access serving/* (cache - system only)
❌ Access metadata/* (system - engineering only)

BI/Dashboard Team:
✅ Read serving/* (S3 direct or cache)
❌ Query analytics/* (should use cache instead)
❌ Access metadata/* (system - engineering only)

Data Engineers:
✅ All layers
✅ Monitor metadata/*
✅ Manage pipeline
```

---

## METADATA FILES

### Structure

每個 Silver/Gold partition 包含 `_metadata.json`:

```json
{
  "table_name": "silver_news",
  "partition_date": "2025-10-18",
  "row_count": 4523,
  "columns": ["id", "data_date", "source", "title", "content", "sentiment_score", "_source", "_ingest_time"],
  "batch_processing": {
    "batch_size": 500,
    "total_batches": 17,
    "total_files_processed": 8439
  },
  "processing_timestamp": "2025-10-18T10:45:23.123456+00:00",
  "date_range": {
    "min": "2025-10-18",
    "max": "2025-10-18"
  }
}
```

### Purpose

| Field | Purpose |
|-------|---------|
| `table_name` | Identify which table |
| `partition_date` | Processing date |
| `row_count` | Data quality check |
| `columns` | Schema validation |
| `batch_processing` | Performance tracking |
| `processing_timestamp` | Audit trail |
| `date_range` | Data coverage |

### Usage

```sql
-- Athena: Check data quality
SELECT row_count, processing_timestamp 
FROM s3_object_metadata
WHERE partition_date = '2025-10-18'
```

---

## QUERY EXAMPLES

### 🔷 Querying LAYER 1: Analytics (Athena)

#### 1. Market Technical Analysis

```sql
-- Query from gold/analytics/market_features/
SELECT 
    symbol,
    data_date,
    close,
    MA_20,
    MA_30,
    RSI_14,
    volatility_7d,
    price_change_pct
FROM gold_analytics.market_features
WHERE partition_date = '2025-10-18'
  AND RSI_14 < 30  -- Oversold condition
ORDER BY symbol, data_date DESC
LIMIT 50
```

**Result:**
```
symbol | data_date  | close  | MA_20  | RSI_14 | volatility_7d
ACB    | 2025-10-18 | 25400  | 25320  | 28.5   | 1.8
VCB    | 2025-10-18 | 28600  | 28450  | 32.1   | 1.5
```

**Use Case:** Traders find oversold stocks for buying signal

---

#### 2. Sector Rotation Analysis

```sql
-- Query from gold/analytics/sector_performance/
SELECT 
    data_date,
    sector,
    avg_price_change_pct,
    avg_volatility,
    RANK() OVER (PARTITION BY data_date ORDER BY avg_price_change_pct DESC) as sector_rank
FROM gold_analytics.sector_performance
WHERE partition_date >= DATE('2025-10-01')
ORDER BY data_date DESC, sector_rank
```

**Use Case:** Portfolio managers understand sector trends

---

#### 3. Macro Indicator Trends

```sql
-- Query from gold/analytics/macro_indicators/
SELECT 
    data_date,
    indicator_name,
    indicator_value,
    MA_7,
    MA_30,
    value_change_pct,
    CASE 
        WHEN value_change_pct > 1.0 THEN 'SPIKE'
        WHEN value_change_pct < -1.0 THEN 'DROP'
        ELSE 'STABLE'
    END as trend
FROM gold_analytics.macro_indicators
WHERE partition_date >= DATE('2025-10-01')
  AND indicator_name IN ('Inflation', 'Gdp')
ORDER BY indicator_name, data_date DESC
```

**Use Case:** Economists track macro changes

---

### 🔶 Querying LAYER 2: Sentiment Analysis (Athena)

#### 4. Sentiment Trends by Source

```sql
-- Query from gold/sentiment_analysis/
SELECT 
    data_date,
    source,
    article_count,
    avg_sentiment,
    positive_count,
    negative_count,
    sentiment_change_pct,
    ROUND(positive_count * 100.0 / article_count, 2) as positive_pct
FROM gold_analytics.sentiment_analysis
WHERE partition_date >= DATE('2025-10-10')
  AND article_count > 50  -- Minimum articles
ORDER BY data_date DESC, avg_sentiment DESC
```

**Result:**
```
data_date  | source     | article_count | avg_sentiment | positive_pct
2025-10-18 | google_cse | 245           | 0.52          | 63.7
2025-10-18 | vnexpress  | 180           | 0.38          | 54.4
```

**Use Case:** Analysts understand market sentiment

---

#### 5. Sentiment Anomalies (Trading Signals)

```sql
-- Detect sentiment spikes (potential trading signals)
SELECT 
    data_date,
    source,
    article_count,
    avg_sentiment,
    sentiment_change_pct,
    ABS(sentiment_change_pct) as abs_change
FROM gold_analytics.sentiment_analysis
WHERE partition_date >= DATE('2025-10-01')
  AND ABS(sentiment_change_pct) > 5.0  -- Significant change
ORDER BY abs_change DESC, data_date DESC
LIMIT 20
```

**Use Case:** Detect sudden sentiment shifts for trading

---

#### 6. Cross-Layer Join: News + Market Analysis

```sql
-- Join analytics/news_summary with analytics/market_features
SELECT 
    m.data_date,
    n.total_articles,
    n.avg_sentiment,
    m.symbol,
    m.close,
    m.price_change_pct,
    m.RSI_14,
    CASE 
        WHEN n.avg_sentiment > 0.4 AND m.RSI_14 < 40 THEN 'BUY_SIGNAL'
        WHEN n.avg_sentiment < -0.3 AND m.RSI_14 > 60 THEN 'SELL_SIGNAL'
        ELSE 'NEUTRAL'
    END as signal
FROM gold_analytics.market_features m
LEFT JOIN gold_analytics.news_summary n
    ON m.data_date = n.data_date
WHERE m.partition_date = '2025-10-18'
  AND n.partition_date = '2025-10-18'
ORDER BY m.data_date DESC, m.symbol
```

**Use Case:** Combined signal for sentiment + technicals

---

### 📊 Creating Athena External Tables

```sql
-- Database setup for Gold Layer
CREATE DATABASE IF NOT EXISTS gold_analytics;

-- Layer 1: Analytics
CREATE EXTERNAL TABLE IF NOT EXISTS gold_analytics.market_features (
    symbol STRING,
    data_date DATE,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume BIGINT,
    price_change_pct DOUBLE,
    MA_5 DOUBLE,
    MA_10 DOUBLE,
    MA_20 DOUBLE,
    MA_30 DOUBLE,
    RSI_14 DOUBLE,
    volatility_7d DOUBLE,
    price_change_5d DOUBLE,
    price_change_10d DOUBLE
)
PARTITIONED BY (partition_date STRING)
STORED AS PARQUET
LOCATION 's3://bankanalystportfolio/gold/analytics/market_features/';

CREATE EXTERNAL TABLE IF NOT EXISTS gold_analytics.sector_performance (
    data_date DATE,
    sector STRING,
    avg_price_change_pct DOUBLE,
    avg_volatility DOUBLE,
    avg_volume DOUBLE
)
PARTITIONED BY (partition_date STRING)
STORED AS PARQUET
LOCATION 's3://bankanalystportfolio/gold/analytics/sector_performance/';

CREATE EXTERNAL TABLE IF NOT EXISTS gold_analytics.news_summary (
    data_date DATE,
    total_articles BIGINT,
    unique_sources BIGINT,
    avg_sentiment DOUBLE,
    articles_positive BIGINT,
    articles_negative BIGINT,
    avg_title_length DOUBLE,
    top_source STRING
)
PARTITIONED BY (partition_date STRING)
STORED AS PARQUET
LOCATION 's3://bankanalystportfolio/gold/analytics/news_summary/';

CREATE EXTERNAL TABLE IF NOT EXISTS gold_analytics.macro_indicators (
    data_date DATE,
    indicator_name STRING,
    indicator_value DOUBLE,
    MA_7 DOUBLE,
    MA_30 DOUBLE,
    value_change DOUBLE,
    value_change_pct DOUBLE,
    indicator_source STRING
)
PARTITIONED BY (partition_date STRING)
STORED AS PARQUET
LOCATION 's3://bankanalystportfolio/gold/analytics/macro_indicators/';

-- Layer 2: Sentiment Analysis
CREATE EXTERNAL TABLE IF NOT EXISTS gold_analytics.sentiment_analysis (
    data_date DATE,
    source STRING,
    article_count BIGINT,
    avg_sentiment DOUBLE,
    positive_count BIGINT,
    negative_count BIGINT,
    neutral_count BIGINT,
    sentiment_change_pct DOUBLE
)
PARTITIONED BY (partition_date STRING)
STORED AS PARQUET
LOCATION 's3://bankanalystportfolio/gold/sentiment_analysis/';

-- Refresh partitions
MSCK REPAIR TABLE gold_analytics.market_features;
MSCK REPAIR TABLE gold_analytics.sector_performance;
MSCK REPAIR TABLE gold_analytics.news_summary;
MSCK REPAIR TABLE gold_analytics.macro_indicators;
MSCK REPAIR TABLE gold_analytics.sentiment_analysis;
```

---

### 🎯 Query Performance Tips

| Query Type | Best Layer | Performance |
|-----------|-----------|-------------|
| Ad-hoc analysis | analytics/ | 1-30s |
| Sentiment trends | sentiment_analysis/ | 1-30s |
| Dashboard loads | serving/ | < 100ms |
| Real-time display | serving/ (cache) | < 50ms |

**Recommendation:**
- ✅ Use `analytics/` for: reports, ad-hoc queries, ML training
- ✅ Use `sentiment_analysis/` for: sentiment-specific analysis
- ✅ Use `serving/` for: dashboards, real-time displays

#### 4. Top Performing Stocks

```sql
SELECT 
    symbol,
    data_date,
    close,
    price_change_pct,
    volume
FROM finance_portfolio.silver_stocks
WHERE data_date = DATE('2025-10-18')
  AND price_change_pct > 5.0
ORDER BY price_change_pct DESC
```

#### 5. Macro Economic Dashboard

```sql
SELECT 
    MAX(CASE WHEN indicator_name = 'Gdp' THEN indicator_value END) as gdp,
    MAX(CASE WHEN indicator_name = 'Inflation' THEN indicator_value END) as inflation,
    MAX(CASE WHEN indicator_name = 'Usd Vnd' THEN indicator_value END) as usd_vnd,
    MAX(CASE WHEN indicator_name = 'Vnindex' THEN indicator_value END) as vnindex,
    MAX(data_date) as latest_date
FROM finance_portfolio.silver_macro
WHERE data_date = (SELECT MAX(data_date) FROM finance_portfolio.silver_macro)
```

---

## DATA FLOW DIAGRAM

```
┌─────────────────────────┐
│   BRONZE LAYER (Raw)    │
├─────────────────────────┤
│ • stocks/*.json         │ ← bronze_stocks.py
│ • news/*.json           │ ← bronze_news.py
│ • macro/*.csv           │ ← bronze_macro.py
│ (150K + 8.4K + 50)      │
└────────────┬────────────┘
             │
             ↓ (ETL: Cleaning, Standardization)
             │
┌─────────────────────────────────────────┐
│    SILVER LAYER (Standardized)          │
├─────────────────────────────────────────┤
│ partition_date=YYYY-MM-DD/              │
│ ├── stocks_data.parquet (3K rows/day)   │ ← bronze_to_silver_v6.py
│ ├── news_cleaned.parquet (4.5K rows)    │ ← bronze_to_silver_macro_news.py
│ └── macro_data.parquet (1.2K rows)      │ ← bronze_to_silver_macro_news.py
└────────────┬────────────────────────────┘
             │
             ↓ (ETL: Feature Engineering, Aggregations)
             │
┌─────────────────────────────────────────┐
│    GOLD LAYER (Analytics Ready)         │
├─────────────────────────────────────────┤
│ partition_date=YYYY-MM-DD/              │
│ ├── market_features/                    │ ← silver_to_gold_macro_news.py (v2.0)
│ │   └── features_merged.parquet         │    (Technical indicators)
│ ├── sentiment_analysis/                 │
│ │   └── sentiment_daily.parquet         │    (News sentiment)
│ ├── news_summary/                       │
│ │   └── news_daily_summary.parquet      │    (News aggregations)
│ ├── macro_indicators/                   │
│ │   └── macro_indicators.parquet        │    (Macro trends)
│ └── sector_performance/                 │
│     └── sector_index.parquet            │    (Sector analysis)
└────────────┬────────────────────────────┘
             │
             ↓ (Query via Athena)
             │
┌─────────────────────────────────────────┐
│    ANALYTICS & BI TOOLS                 │
├─────────────────────────────────────────┤
│ • Athena (SQL Queries)                  │
│ • Tableau / PowerBI (Dashboards)        │
│ • Python / Pandas (Data Analysis)       │
│ • Chatbot (Natural Language)            │
└─────────────────────────────────────────┘
```

---

## PARTITION STRATEGY BENEFITS

### ✅ Query Performance

```sql
-- Partition pruning: Only reads 1 day of data
SELECT * FROM silver_news 
WHERE partition_date = '2025-10-18'  -- Scans only 20MB instead of 100GB+

-- Cost: ~0.01 $ vs ~0.5 $
```

### ✅ Incremental Updates

```
Daily Process:
09:00 UTC → Bronze collection (stocks, news, macro)
11:00 UTC → Silver transformation (partition_date=today)
18:00 UTC → Gold transformation (features, aggregations)

Each partition is independent → Easy parallelization
```

### ✅ Data Retention

```sql
-- Delete old partitions to save storage
ALTER TABLE silver_news DROP PARTITION (partition_date='2024-01-01')

-- Automatic via lifecycle policies
```

### ✅ Partition Discovery

```
Athena automatically detects:
- s3://bankanalystportfolio/silver/news/partition_date=2025-10-18/
- s3://bankanalystportfolio/silver/news/partition_date=2025-10-17/
- s3://bankanalystportfolio/silver/news/partition_date=2025-10-16/
...

No manual manifest updates needed!
```

---

## STORAGE ESTIMATES

### Current Size

| Layer | Type | Count | Size/Day | Total |
|-------|------|-------|----------|-------|
| **Bronze** | JSON | 158,439 | ~100 MB | - |
| **Bronze** | CSV | 50 | ~10 MB | - |
| **Silver** | Stocks | 3,000 | ~40 MB | - |
| **Silver** | News | 4,500 | ~30 MB | - |
| **Silver** | Macro | 1,200 | ~8 MB | - |
| **Gold** | Features | 3,000 | ~35 MB | - |
| **Gold** | Sentiment | 500 | ~5 MB | - |
| **Gold** | Macro | 1,200 | ~8 MB | - |

### Growth per Month

- Silver: ~2.3 GB/month
- Gold: ~1.5 GB/month
- **Total: ~3.8 GB/month**

### Cost Estimate (AWS S3)

- Storage: **~$0.10/month** (first 1TB)
- Athena queries: **~$5-10/month** (100-200 queries/month)

---

## NEXT STEPS

1. **Set up Athena Database**
   ```sql
   CREATE DATABASE IF NOT EXISTS finance_portfolio
   ```

2. **Create External Tables**
   ```sql
   CREATE EXTERNAL TABLE silver_news (
       id STRING,
       data_date DATE,
       source STRING,
       title STRING,
       content STRING,
       sentiment_score DOUBLE
   )
   PARTITIONED BY (partition_date STRING)
   STORED AS PARQUET
   LOCATION 's3://bankanalystportfolio/silver/news/'
   ```

3. **Schedule Daily ETL**
   - Airflow DAGs (09:00, 11:00, 18:00 UTC)
   - Lambda functions (alternative)

4. **Enable Chatbot Integration**
   - Connect Athena connector to FastAPI backend
   - Deploy web executor with API endpoints

5. **Set up Monitoring**
   - CloudWatch logs
   - Data quality checks
   - Partition status tracking

---

**Document Version:** v1.0  
**Last Updated:** 2025-10-18  
**Status:** Production Ready
