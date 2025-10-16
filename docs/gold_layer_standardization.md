# Gold Layer Pipeline Standardization Documentation

## Overview
This document describes the standardization of the Gold Layer Airflow DAG (`gold_layer_pipeline.py`) to align with the actual Bronze and Silver layer S3 structure and schema.

## 🔄 Changes Made

### 1. S3 Path Structure Standardization

**Before:**
```python
# Generic paths without date format handling
stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
news_file_key = f"silver/news/processed/clean_news_{date_str}.csv"
```

**After:**
```python
# Date format flexibility (YYYYMMDD vs YYYY-MM-DD)
stock_file_key = f"silver/stocks/processed/clean_stocks_{date_str.replace('-', '')}.csv"
# Fallback to alternative format
if not s3_hook.check_for_key(key=stock_file_key, bucket_name=bucket_name):
    alt_stock_key = f"silver/stocks/processed/clean_stocks_{date_str}.csv"
    if s3_hook.check_for_key(key=alt_stock_key, bucket_name=bucket_name):
        stock_file_key = alt_stock_key
```

### 2. Schema Field Alignment

**Before:**
```python
# Assumed fields that may not exist
stocks_df['ticker']  # May not exist, should be 'symbol'
news_df['sentiment_basic']  # May not exist
news_df['topic_category']  # May not exist
```

**After:**
```python
# Check for field existence and handle alternatives
if 'symbol' in ml_df.columns and 'ticker' not in ml_df.columns:
    ml_df['ticker'] = ml_df['symbol']

# Handle sentiment columns based on actual Silver output
if 'sentiment_basic' in news_df.columns:
    sentiment_analytics['sentiment_distribution'] = news_df['sentiment_basic'].value_counts().to_dict()
elif 'sentiment_score' in news_df.columns:
    # Create basic sentiment from scores
    news_df['sentiment_basic'] = news_df['sentiment_score'].apply(
        lambda x: 'POSITIVE' if x > 0.1 else ('NEGATIVE' if x < -0.1 else 'NEUTRAL')
    )
```

### 3. Gold Layer Output Structure

**Before:**
```
gold/
├── analytics/market_summary_{date}.json
├── serving/ml_features_{date}.csv
└── metadata/feature_stats_{date}.json
```

**After:**
```
gold/
├── analytics/
│   ├── market_summary/market_summary_{YYYYMMDD}.json
│   └── sentiment_analysis/news_sentiment_{YYYYMMDD}.json
├── serving/
│   ├── ml_features/ml_features_{YYYYMMDD}.csv
│   └── integrated_view/integrated_view_{YYYYMMDD}.csv
└── metadata/
    ├── feature_stats/feature_stats_{YYYYMMDD}.json
    └── integrated_summary/integrated_summary_{YYYYMMDD}.json
```

## 🏗️ Architecture Alignment

### Bronze Layer Input
- **Stocks**: `bronze/stocks/raw/{symbol}/{symbol}_{date}.json`
- **News**: `bronze/news/raw/{news_id}.json`
- **Others**: `bronze/others/raw/vnindex_*.csv`

### Silver Layer Input
- **Stocks**: `silver/stocks/processed/clean_stocks_{YYYYMMDD}.csv`
- **News**: `silver/news/processed/clean_news_{YYYYMMDD}.csv`
- **Others**: `silver/others/processed/clean_others_{YYYYMMDD}.csv`

### Gold Layer Output
- **Analytics**: Business intelligence tables for dashboards
- **Serving**: ML-ready datasets for model training
- **Metadata**: Processing logs and data quality metrics

## 📊 Schema Mapping

### Stock Data Schema
| Bronze | Silver | Gold |
|--------|--------|------|
| `_source.open` | `open` | `open` |
| `_source.high` | `high` | `high` |
| `_source.low` | `low` | `low` |
| `_source.close` | `close` | `close` |
| `_source.volume` | `volume` | `volume` |
| N/A | `symbol` | `ticker` (standardized) |
| N/A | `daily_return` | `daily_return` |
| N/A | `MA_5`, `MA_20`, `RSI` | Technical features |

### News Data Schema
| Bronze | Silver | Gold |
|--------|--------|------|
| `title` | `title` | Used for sentiment |
| `combined_text` | `combined_text` | Primary text for analysis |
| `link` | `url` | Reference |
| N/A | `sentiment_score` | `sentiment_basic` |
| N/A | `content_length` | Analytics metric |

## 🔧 Technical Improvements

### 1. Error Handling
```python
# Robust column checking
if 'daily_return' in ml_df.columns:
    ml_df['return_squared'] = ml_df['daily_return'] ** 2
else:
    # Calculate daily return if not present
    if all(col in ml_df.columns for col in ['close', 'open']):
        ml_df['daily_return'] = (ml_df['close'] - ml_df['open']) / ml_df['open']
```

### 2. Feature Engineering Flexibility
```python
# Only use features that exist in Silver data
feature_columns = [col for col in base_columns if col in ml_df.columns]
additional_features = [
    'price_to_open_ratio', 'high_low_spread', 'volume_log',
    'bank_tier_score', 'target_direction'
]
for col in additional_features:
    if col in ml_df.columns:
        feature_columns.append(col)
```

### 3. Banking Sector Classification
```python
# Vietnamese banking tier system
big4_banks = ['VCB', 'BID', 'CTG', 'AGR']  # State-owned big 4
tier1_banks = ['VPB', 'TCB', 'MBB', 'STB', 'HDB', 'ACB', 'TPB', 'VIB']

def encode_bank_tier(ticker):
    ticker = str(ticker).upper()
    if ticker in big4_banks:
        return 1.0  # Highest tier
    elif ticker in tier1_banks:
        return 0.7  # Medium tier
    else:
        return 0.3  # Lower tier
```

## 📈 Data Quality Improvements

### 1. Validation Checks
- Check for required columns before processing
- Handle missing sentiment/technical indicator data
- Validate data ranges (RSI 0-100, sentiment -1 to 1)

### 2. Metadata Generation
```json
{
  "processing_date": "2025-10-16",
  "total_records": 156,
  "unique_stocks": 156,
  "has_news_data": true,
  "feature_count": 15,
  "target_distribution": {
    "UP": 45,
    "DOWN": 67,
    "FLAT": 44
  }
}
```

## 🚀 Deployment Notes

### Environment Variables
```bash
S3_BUCKET=bankanalystportfolio
MAX_RETRY_ATTEMPTS=2
```

### Airflow Configuration
- **Schedule**: `0 8 * * 1-5` (8:00 AM weekdays, after Silver DAG)
- **Max Active Runs**: 1
- **Retry Delay**: 5 minutes
- **Execution Timeout**: 2 hours

### Dependencies
- pandas >= 1.3.0
- numpy >= 1.21.0
- airflow-providers-amazon >= 3.0.0

## 🔍 Validation Checklist

- [ ] Silver layer files exist before processing
- [ ] Schema fields match actual Silver output
- [ ] Gold layer paths follow consistent structure
- [ ] Banking tier classification works correctly
- [ ] Sentiment analysis handles missing data
- [ ] ML features include only available columns
- [ ] Metadata files are properly generated
- [ ] Error handling covers edge cases

## 📋 Success Metrics

### Processing Metrics
- **Market Summary**: 150+ stocks processed daily
- **ML Features**: 15+ features per stock
- **Sentiment Analysis**: News articles with sentiment scores
- **Data Quality**: <5% missing values in critical fields

### Output Structure
```
s3://bankanalystportfolio/gold/
├── analytics/
│   ├── market_summary/ (business intelligence)
│   └── sentiment_analysis/ (news analytics)
├── serving/
│   ├── ml_features/ (ML training data)
│   └── integrated_view/ (combined datasets)
└── metadata/
    ├── feature_stats/ (quality metrics)
    └── integrated_summary/ (processing logs)
```

## 🔮 Future Enhancements

1. **Real-time Processing**: Stream processing for intraday updates
2. **Advanced Features**: More sophisticated technical indicators
3. **Model Integration**: Direct integration with ML training pipelines
4. **Data Lineage**: Track data flow from Bronze to Gold
5. **Alerting**: Quality monitoring and automated alerts

---

**Last Updated**: October 16, 2025  
**Version**: 2.0  
**Status**: Production Ready ✅