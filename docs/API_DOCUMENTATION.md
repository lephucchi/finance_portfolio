# 📚 Vietnam Stock Market API - Frontend Developer Guide

**Base URL:** `http://localhost:8000/api/v1`  
**Version:** 1.0  
**Status:** ✅ Production Ready (13/14 endpoints working)  
**Last Updated:** October 30, 2025

---

## 🚀 Quick Start

### Authentication
Currently **no authentication required** (development mode).

### Base Response Format

All endpoints return this structure:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response Format

```json
{
  "success": false,
  "data": null,
  "message": "Error message",
  "detail": "Detailed error information"
}
```

### Available Data Range
- **Market Data:** Oct 18-30, 2025 (13 days)
- **Stock Symbols:** 30+ symbols (VIC, VHM, VCB, FPT, HPG, etc.)
- **Macro Indicators:** 39 indicators

---

## 📖 API Endpoints

### Table of Contents
- [1. Health Check](#1-health-check)
- [2. Market Data (4 endpoints)](#2-market-data)
- [3. Sentiment Analysis (2 endpoints)](#3-sentiment-analysis)
- [4. Macro Economics (4 endpoints)](#4-macro-economics)
- [5. Dashboard Analytics (2 endpoints)](#5-dashboard-analytics)

---

## 1. Health Check

### GET /health

Check API health status.

**Parameters:** None

**Response Time:** ~2s

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-10-30T10:30:00Z"
  },
  "message": "API is healthy"
}
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/v1/health');
const data = await response.json();
console.log(data.data.status); // "healthy"
```

**Example (curl):**
```bash
curl http://localhost:8000/api/v1/health
```

---

## 2. Market Data

### 2.1 GET /market/stocks

Get stock market data for date range.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string (YYYY-MM-DD) | Yes | Start date |
| `end_date` | string (YYYY-MM-DD) | Yes | End date |
| `symbols` | string | No | Comma-separated symbols (e.g., "VIC,VHM,VCB") |

**Response Time:** 
- All symbols: ~7-8s
- Filtered (2-3 symbols): ~5s

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "VIC",
      "data_date": "2025-10-30",
      "open": 179700,
      "high": 180500,
      "low": 178900,
      "close": 180200,
      "volume": 3853015,
      "ma_20": 175300.5,
      "ma_50": 168500.2,
      "price_change_pct": 2.35,
      "volatility_7d": 0.023
    },
    ...
  ],
  "message": "Stock data retrieved successfully"
}
```

**Example (JavaScript):**
```javascript
// Get all symbols
const getAllStocks = async (startDate, endDate) => {
  const url = `http://localhost:8000/api/v1/market/stocks?start_date=${startDate}&end_date=${endDate}`;
  const response = await fetch(url);
  const data = await response.json();
  return data.data; // Array of stock records
};

// Get specific symbols
const getFilteredStocks = async (startDate, endDate, symbols) => {
  const symbolsStr = symbols.join(',');
  const url = `http://localhost:8000/api/v1/market/stocks?start_date=${startDate}&end_date=${endDate}&symbols=${symbolsStr}`;
  const response = await fetch(url);
  const data = await response.json();
  return data.data;
};

// Usage
const stocks = await getAllStocks('2025-10-25', '2025-10-30');
const vicData = await getFilteredStocks('2025-10-25', '2025-10-30', ['VIC', 'VHM']);
```

**Example (Python):**
```python
import requests

def get_stocks(start_date, end_date, symbols=None):
    params = {
        'start_date': start_date,
        'end_date': end_date
    }
    if symbols:
        params['symbols'] = ','.join(symbols)
    
    response = requests.get(
        'http://localhost:8000/api/v1/market/stocks',
        params=params
    )
    data = response.json()
    return data['data']

# Usage
stocks = get_stocks('2025-10-25', '2025-10-30')
vic_stocks = get_stocks('2025-10-25', '2025-10-30', ['VIC', 'VHM'])
```

**Example (curl):**
```bash
# All symbols
curl "http://localhost:8000/api/v1/market/stocks?start_date=2025-10-25&end_date=2025-10-30"

# Specific symbols
curl "http://localhost:8000/api/v1/market/stocks?start_date=2025-10-25&end_date=2025-10-30&symbols=VIC,VHM,VCB"
```

---

### 2.2 GET /market/technical-indicators

Get technical indicators for a specific stock.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Stock symbol (e.g., "VIC") |
| `start_date` | string | Yes | Start date (YYYY-MM-DD) |
| `end_date` | string | Yes | End date (YYYY-MM-DD) |

**Response Time:** ~4-5s

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "VIC",
    "indicators": [
      {
        "date": "2025-10-30",
        "ma_20": 175300.5,
        "ma_50": 168500.2,
        "rsi_14": 65.5,
        "macd": 1.23,
        "macd_signal": 0.98,
        "bollinger_upper": 182000,
        "bollinger_middle": 175000,
        "bollinger_lower": 168000,
        "volatility_7d": 0.023,
        "volume_ma_20": 3500000
      },
      ...
    ]
  },
  "message": "Technical indicators retrieved"
}
```

**Technical Indicators Explained:**

| Indicator | Description | Interpretation |
|-----------|-------------|----------------|
| `ma_20` | 20-day Moving Average | Trend direction |
| `ma_50` | 50-day Moving Average | Long-term trend |
| `rsi_14` | Relative Strength Index (0-100) | >70 overbought, <30 oversold |
| `macd` | MACD line | Momentum indicator |
| `macd_signal` | Signal line | Buy/sell signals |
| `bollinger_upper` | Upper Bollinger Band | Price ceiling |
| `bollinger_lower` | Lower Bollinger Band | Price floor |
| `volatility_7d` | 7-day volatility | Risk measure |

**Example (React Hook):**
```typescript
import { useState, useEffect } from 'react';

interface TechnicalIndicator {
  date: string;
  ma_20: number;
  ma_50: number;
  rsi_14: number;
  // ... other fields
}

function useTechnicalIndicators(symbol: string, startDate: string, endDate: string) {
  const [data, setData] = useState<TechnicalIndicator[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:8000/api/v1/market/technical-indicators?` +
          `symbol=${symbol}&start_date=${startDate}&end_date=${endDate}`
        );
        const result = await response.json();
        
        if (result.success) {
          setData(result.data.indicators);
        } else {
          setError(result.message);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [symbol, startDate, endDate]);

  return { data, loading, error };
}

// Usage in component
function StockChart({ symbol }: { symbol: string }) {
  const { data, loading, error } = useTechnicalIndicators(
    symbol,
    '2025-10-25',
    '2025-10-30'
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {data.map(indicator => (
        <div key={indicator.date}>
          MA20: {indicator.ma_20}, RSI: {indicator.rsi_14}
        </div>
      ))}
    </div>
  );
}
```

---

### 2.3 GET /market/sector-performance

Get sector performance analysis.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | Yes | Start date |
| `end_date` | string | Yes | End date |

**Response Time:** ~2-3s

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "sector": "Banking",
      "avg_change_pct": 2.5,
      "total_volume": 125000000,
      "stock_count": 15,
      "top_gainers": ["VCB", "BID", "CTG"],
      "top_losers": ["STB"]
    },
    {
      "sector": "Real Estate",
      "avg_change_pct": 3.2,
      "total_volume": 98000000,
      "stock_count": 12,
      "top_gainers": ["VHM", "NVL"],
      "top_losers": ["DXG"]
    }
  ],
  "message": "Sector performance retrieved"
}
```

**Example (Chart.js Integration):**
```javascript
import { Chart } from 'chart.js';

async function createSectorChart() {
  const response = await fetch(
    'http://localhost:8000/api/v1/market/sector-performance?' +
    'start_date=2025-10-18&end_date=2025-10-30'
  );
  const result = await response.json();
  const sectors = result.data;

  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: sectors.map(s => s.sector),
      datasets: [{
        label: 'Avg Change %',
        data: sectors.map(s => s.avg_change_pct),
        backgroundColor: sectors.map(s => 
          s.avg_change_pct > 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)'
        )
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Sector Performance'
        }
      }
    }
  });
}
```

---

## 3. Sentiment Analysis

### 3.1 GET /sentiment/summary

Get daily sentiment summary from news articles.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | Yes | Start date |
| `end_date` | string | Yes | End date |

**Response Time:** ~4-5s

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": [
      {
        "date": "2025-10-30",
        "positive_count": 45,
        "negative_count": 12,
        "neutral_count": 33,
        "avg_sentiment": 0.65,
        "total_articles": 90,
        "positive_pct": 50.0,
        "negative_pct": 13.3,
        "neutral_pct": 36.7
      },
      ...
    ],
    "overall": {
      "total_articles": 450,
      "avg_sentiment": 0.58,
      "dominant_sentiment": "positive"
    }
  },
  "message": "Sentiment summary retrieved"
}
```

**Sentiment Score Guide:**
- `>= 0.3`: Positive
- `-0.3 to 0.3`: Neutral
- `< -0.3`: Negative

**Example (Vue.js Component):**
```vue
<template>
  <div class="sentiment-dashboard">
    <h2>Market Sentiment</h2>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <div class="sentiment-card">
        <h3>Overall Sentiment</h3>
        <div class="sentiment-score" :class="sentimentClass">
          {{ overall.avg_sentiment.toFixed(2) }}
        </div>
        <p>{{ overall.total_articles }} articles analyzed</p>
      </div>
      
      <div class="daily-sentiment">
        <div v-for="day in summary" :key="day.date" class="day-card">
          <p>{{ day.date }}</p>
          <div class="sentiment-breakdown">
            <span class="positive">👍 {{ day.positive_pct.toFixed(1) }}%</span>
            <span class="neutral">😐 {{ day.neutral_pct.toFixed(1) }}%</span>
            <span class="negative">👎 {{ day.negative_pct.toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      summary: [],
      overall: null,
      loading: true,
      error: null
    };
  },
  computed: {
    sentimentClass() {
      if (!this.overall) return '';
      const score = this.overall.avg_sentiment;
      if (score >= 0.3) return 'positive';
      if (score <= -0.3) return 'negative';
      return 'neutral';
    }
  },
  async mounted() {
    await this.fetchSentiment();
  },
  methods: {
    async fetchSentiment() {
      try {
        this.loading = true;
        const response = await fetch(
          'http://localhost:8000/api/v1/sentiment/summary?' +
          'start_date=2025-10-25&end_date=2025-10-30'
        );
        const result = await response.json();
        
        if (result.success) {
          this.summary = result.data.summary;
          this.overall = result.data.overall;
        } else {
          this.error = result.message;
        }
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.sentiment-score {
  font-size: 3em;
  font-weight: bold;
}
.sentiment-score.positive { color: #22c55e; }
.sentiment-score.negative { color: #ef4444; }
.sentiment-score.neutral { color: #f59e0b; }
</style>
```

---

### 3.2 GET /sentiment/trend

Get sentiment trend over time.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | Yes | Start date |
| `end_date` | string | Yes | End date |
| `interval` | string | No | "daily" (default), "weekly", "monthly" |

**Response Time:** ~4s

**Response:**
```json
{
  "success": true,
  "data": {
    "interval": "daily",
    "trend": [
      {
        "period": "2025-10-30",
        "avg_sentiment": 0.65,
        "article_count": 90,
        "positive_pct": 50.0,
        "negative_pct": 13.3,
        "neutral_pct": 36.7
      },
      ...
    ]
  },
  "message": "Sentiment trend retrieved"
}
```

**Example (Plotly Chart):**
```javascript
import Plotly from 'plotly.js-dist';

async function createSentimentTrendChart() {
  const response = await fetch(
    'http://localhost:8000/api/v1/sentiment/trend?' +
    'start_date=2025-10-18&end_date=2025-10-30&interval=daily'
  );
  const result = await response.json();
  const trend = result.data.trend;

  const trace = {
    x: trend.map(t => t.period),
    y: trend.map(t => t.avg_sentiment),
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Sentiment Score',
    line: {
      color: 'rgb(34, 197, 94)',
      width: 2
    },
    marker: {
      size: 8
    }
  };

  const layout = {
    title: 'Market Sentiment Trend',
    xaxis: { title: 'Date' },
    yaxis: { 
      title: 'Sentiment Score',
      range: [-1, 1]
    },
    shapes: [
      // Positive threshold line
      {
        type: 'line',
        x0: trend[0].period,
        x1: trend[trend.length - 1].period,
        y0: 0.3,
        y1: 0.3,
        line: { color: 'rgba(34, 197, 94, 0.3)', dash: 'dash' }
      },
      // Negative threshold line
      {
        type: 'line',
        x0: trend[0].period,
        x1: trend[trend.length - 1].period,
        y0: -0.3,
        y1: -0.3,
        line: { color: 'rgba(239, 68, 68, 0.3)', dash: 'dash' }
      }
    ]
  };

  Plotly.newPlot('sentiment-chart', [trace], layout);
}
```

---

## 4. Macro Economics

### 4.1 GET /macro/indicators

Get all macro economic indicators.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | Yes | Start date |
| `end_date` | string | Yes | End date |
| `indicators` | string | No | Comma-separated indicator names |

**Response Time:** ~4-5s

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-10-30",
      "indicator_name": "CPI",
      "indicator_value": 118.5,
      "value_change_pct": 3.2,
      "ma_7": 118.2,
      "ma_30": 117.8
    },
    {
      "date": "2025-10-30",
      "indicator_name": "GDP_GROWTH",
      "indicator_value": 6.8,
      "value_change_pct": 0.5,
      "ma_7": 6.7,
      "ma_30": 6.5
    },
    ...
  ],
  "message": "Macro indicators retrieved"
}
```

**Common Indicators:**
- `CPI` - Consumer Price Index
- `GDP_GROWTH` - GDP Growth Rate
- `UNEMPLOYMENT_RATE` - Unemployment Rate
- `INTEREST_RATE` - Base Interest Rate
- `INFLATION_RATE` - Inflation Rate
- `USD_VND` - USD to VND exchange rate
- `EUR_VND` - EUR to VND exchange rate
- `JPY_VND` - JPY to VND exchange rate

**Example (TypeScript):**
```typescript
interface MacroIndicator {
  date: string;
  indicator_name: string;
  indicator_value: number;
  value_change_pct: number;
  ma_7: number;
  ma_30: number;
}

async function getMacroIndicators(
  startDate: string,
  endDate: string,
  indicators?: string[]
): Promise<MacroIndicator[]> {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate
  });
  
  if (indicators) {
    params.append('indicators', indicators.join(','));
  }

  const response = await fetch(
    `http://localhost:8000/api/v1/macro/indicators?${params}`
  );
  const result = await response.json();
  return result.data;
}

// Usage
const allIndicators = await getMacroIndicators('2025-10-25', '2025-10-30');
const specific = await getMacroIndicators('2025-10-25', '2025-10-30', ['CPI', 'GDP_GROWTH']);
```

---

### 4.2 GET /macro/available-indicators

Get list of all available macro indicators.

**Parameters:** None

**Response Time:** ~2s

**Response:**
```json
{
  "success": true,
  "data": {
    "indicators": [
      {
        "name": "CPI",
        "description": "Consumer Price Index",
        "unit": "index",
        "category": "inflation",
        "available_from": "2025-10-18"
      },
      {
        "name": "GDP_GROWTH",
        "description": "GDP Growth Rate",
        "unit": "percent",
        "category": "growth",
        "available_from": "2025-10-18"
      },
      ...
    ],
    "total_count": 39
  },
  "message": "Available indicators retrieved"
}
```

**Example:**
```javascript
async function getAvailableIndicators() {
  const response = await fetch(
    'http://localhost:8000/api/v1/macro/available-indicators'
  );
  const result = await response.json();
  return result.data.indicators;
}

// Create dropdown
const indicators = await getAvailableIndicators();
const select = document.getElementById('indicator-select');

indicators.forEach(indicator => {
  const option = document.createElement('option');
  option.value = indicator.name;
  option.textContent = `${indicator.description} (${indicator.unit})`;
  select.appendChild(option);
});
```

---

### 4.3 GET /macro/indicator/{indicator_name}

Get time series for specific indicator.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `indicator_name` | string | Yes | Indicator name (path parameter) |
| `start_date` | string | Yes | Start date |
| `end_date` | string | Yes | End date |

**Response Time:** ~4s

**Response:**
```json
{
  "success": true,
  "data": {
    "indicator_name": "CPI",
    "unit": "index",
    "data_points": [
      {
        "date": "2025-10-30",
        "value": 118.5,
        "change_pct": 3.2,
        "ma_7": 118.2,
        "ma_30": 117.8
      },
      ...
    ],
    "statistics": {
      "min": 115.2,
      "max": 118.5,
      "avg": 117.3,
      "std_dev": 1.2
    }
  },
  "message": "Indicator time series retrieved"
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/macro/indicator/CPI?start_date=2025-10-25&end_date=2025-10-30"
curl "http://localhost:8000/api/v1/macro/indicator/USD_VND?start_date=2025-10-25&end_date=2025-10-30"
```

---

### 4.4 GET /macro/forex

Get forex exchange rates.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | Yes | Start date |
| `end_date` | string | Yes | End date |

**Response Time:** ~4-5s

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-10-30",
      "currency_pair": "USD/VND",
      "rate": 24500,
      "change_pct": 0.12,
      "ma_7": 24480,
      "ma_30": 24450
    },
    {
      "date": "2025-10-30",
      "currency_pair": "EUR/VND",
      "rate": 26800,
      "change_pct": -0.05,
      "ma_7": 26820,
      "ma_30": 26750
    },
    ...
  ],
  "message": "Forex rates retrieved"
}
```

**Example (React Currency Widget):**
```tsx
import { useState, useEffect } from 'react';

interface ForexRate {
  date: string;
  currency_pair: string;
  rate: number;
  change_pct: number;
}

export function ForexWidget() {
  const [rates, setRates] = useState<ForexRate[]>([]);

  useEffect(() => {
    fetch(
      'http://localhost:8000/api/v1/macro/forex?' +
      'start_date=2025-10-30&end_date=2025-10-30'
    )
      .then(res => res.json())
      .then(data => setRates(data.data));
  }, []);

  return (
    <div className="forex-widget">
      <h3>Exchange Rates</h3>
      {rates.map(rate => (
        <div key={rate.currency_pair} className="rate-item">
          <span className="currency">{rate.currency_pair}</span>
          <span className="value">{rate.rate.toLocaleString()}</span>
          <span className={rate.change_pct >= 0 ? 'up' : 'down'}>
            {rate.change_pct >= 0 ? '↑' : '↓'} {Math.abs(rate.change_pct).toFixed(2)}%
          </span>
        </div>
      ))}
    </div>
  );
}
```

---

## 5. Dashboard Analytics

### 5.1 GET /dashboard/summary

Get comprehensive dashboard summary for a specific date.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date_` | string | No | Query date (YYYY-MM-DD), defaults to today |

**Response Time:** ~9-12s (aggregates multiple tables)

**Response:**
```json
{
  "success": true,
  "data": {
    "date": "2025-10-30",
    "market": {
      "total_stocks": 30,
      "market_change_pct": 0.42,
      "avg_sentiment": 0.65,
      "total_volume": 480540000,
      "advancing": 18,
      "declining": 9,
      "unchanged": 3
    },
    "top_gainers": [
      {
        "symbol": "VIC",
        "change_pct": 6.89,
        "close": 180200,
        "volume": 3853015
      },
      {
        "symbol": "VHM",
        "change_pct": 5.32,
        "close": 65300,
        "volume": 8920000
      }
    ],
    "top_losers": [
      {
        "symbol": "STB",
        "change_pct": -3.45,
        "close": 28500,
        "volume": 12450000
      }
    ],
    "sentiment": {
      "avg_score": 0.65,
      "positive_pct": 50.0,
      "total_articles": 90
    },
    "macro": {
      "cpi": 118.5,
      "usd_vnd": 24500
    },
    "latest_update": "2025-10-30T10:30:00Z"
  },
  "message": "Dashboard summary retrieved"
}
```

**Example (Complete Dashboard):**
```javascript
async function loadDashboard(date) {
  const response = await fetch(
    `http://localhost:8000/api/v1/dashboard/summary?date_=${date}`
  );
  const result = await response.json();
  const data = result.data;

  // Update market overview
  document.getElementById('total-stocks').textContent = data.market.total_stocks;
  document.getElementById('market-change').textContent = 
    `${data.market.market_change_pct.toFixed(2)}%`;
  document.getElementById('market-change').className = 
    data.market.market_change_pct >= 0 ? 'positive' : 'negative';

  // Update top gainers
  const gainersHtml = data.top_gainers.map(stock => `
    <div class="stock-item">
      <span class="symbol">${stock.symbol}</span>
      <span class="price">${stock.close.toLocaleString()}</span>
      <span class="change positive">+${stock.change_pct.toFixed(2)}%</span>
    </div>
  `).join('');
  document.getElementById('top-gainers').innerHTML = gainersHtml;

  // Update top losers
  const losersHtml = data.top_losers.map(stock => `
    <div class="stock-item">
      <span class="symbol">${stock.symbol}</span>
      <span class="price">${stock.close.toLocaleString()}</span>
      <span class="change negative">${stock.change_pct.toFixed(2)}%</span>
    </div>
  `).join('');
  document.getElementById('top-losers').innerHTML = losersHtml;

  // Update sentiment indicator
  const sentimentColor = data.sentiment.avg_score >= 0.3 ? 'green' : 
                        data.sentiment.avg_score <= -0.3 ? 'red' : 'yellow';
  document.getElementById('sentiment-indicator').style.backgroundColor = sentimentColor;
  document.getElementById('sentiment-score').textContent = 
    data.sentiment.avg_score.toFixed(2);

  // Update macro indicators
  document.getElementById('cpi').textContent = data.macro.cpi;
  document.getElementById('usd-vnd').textContent = data.macro.usd_vnd.toLocaleString();
}

// Load today's dashboard
loadDashboard('2025-10-30');
```

---

### 5.2 GET /dashboard/correlation

Get correlation analysis between sentiment, macro, and market.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | Yes | Start date |
| `end_date` | string | Yes | End date |

**Response Time:** ~7-8s

**Response:**
```json
{
  "success": true,
  "data": {
    "period": {
      "start": "2025-10-25",
      "end": "2025-10-30"
    },
    "data": [
      {
        "data_date": "2025-10-30",
        "symbol": "VIC",
        "price_change_pct": 2.35,
        "avg_sentiment": 0.65,
        "indicator_value": 118.5
      },
      ...
    ],
    "correlations": {
      "sentiment_vs_market": 0.65,
      "macro_vs_market": -0.23
    }
  },
  "message": "Correlation analysis retrieved"
}
```

**Example (Correlation Heatmap):**
```javascript
import Plotly from 'plotly.js';

async function createCorrelationHeatmap() {
  const response = await fetch(
    'http://localhost:8000/api/v1/dashboard/correlation?' +
    'start_date=2025-10-18&end_date=2025-10-30'
  );
  const result = await response.json();
  
  // Calculate correlation matrix
  const data = result.data.data;
  const correlations = calculateCorrelations(data);

  const heatmapData = [{
    z: correlations.matrix,
    x: ['Market', 'Sentiment', 'Macro'],
    y: ['Market', 'Sentiment', 'Macro'],
    type: 'heatmap',
    colorscale: [
      [0, 'rgb(239, 68, 68)'],
      [0.5, 'rgb(255, 255, 255)'],
      [1, 'rgb(34, 197, 94)']
    ],
    zmin: -1,
    zmax: 1
  }];

  const layout = {
    title: 'Correlation Analysis',
    annotations: []
  };

  // Add correlation values as text
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      layout.annotations.push({
        x: j,
        y: i,
        text: correlations.matrix[i][j].toFixed(2),
        showarrow: false,
        font: { color: 'white' }
      });
    }
  }

  Plotly.newPlot('correlation-heatmap', heatmapData, layout);
}
```

---

## 📊 Complete Integration Examples

### Example 1: Stock Portfolio Tracker

```typescript
import { useState, useEffect } from 'react';

interface Portfolio {
  symbol: string;
  shares: number;
  buyPrice: number;
}

function PortfolioTracker() {
  const [portfolio] = useState<Portfolio[]>([
    { symbol: 'VIC', shares: 100, buyPrice: 175000 },
    { symbol: 'VHM', shares: 200, buyPrice: 60000 },
    { symbol: 'VCB', shares: 50, buyPrice: 85000 }
  ]);
  const [currentPrices, setCurrentPrices] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPrices() {
      const symbols = portfolio.map(p => p.symbol).join(',');
      const today = new Date().toISOString().split('T')[0];
      
      const response = await fetch(
        `http://localhost:8000/api/v1/market/stocks?` +
        `start_date=${today}&end_date=${today}&symbols=${symbols}`
      );
      const result = await response.json();
      
      const prices: Record<string, number> = {};
      result.data.forEach((stock: any) => {
        prices[stock.symbol] = stock.close;
      });
      
      setCurrentPrices(prices);
      setLoading(false);
    }

    fetchPrices();
    const interval = setInterval(fetchPrices, 60000); // Update every minute
    return () => clearInterval(interval);
  }, [portfolio]);

  const calculateMetrics = () => {
    let totalCost = 0;
    let totalValue = 0;

    portfolio.forEach(position => {
      totalCost += position.shares * position.buyPrice;
      totalValue += position.shares * (currentPrices[position.symbol] || 0);
    });

    return {
      totalCost,
      totalValue,
      profit: totalValue - totalCost,
      profitPct: ((totalValue - totalCost) / totalCost) * 100
    };
  };

  if (loading) return <div>Loading portfolio...</div>;

  const metrics = calculateMetrics();

  return (
    <div className="portfolio">
      <h2>My Portfolio</h2>
      
      <div className="summary">
        <div className="metric">
          <label>Total Value</label>
          <span>{metrics.totalValue.toLocaleString()} VND</span>
        </div>
        <div className="metric">
          <label>Profit/Loss</label>
          <span className={metrics.profit >= 0 ? 'profit' : 'loss'}>
            {metrics.profit.toLocaleString()} VND ({metrics.profitPct.toFixed(2)}%)
          </span>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Shares</th>
            <th>Buy Price</th>
            <th>Current Price</th>
            <th>P/L</th>
          </tr>
        </thead>
        <tbody>
          {portfolio.map(position => {
            const currentPrice = currentPrices[position.symbol] || 0;
            const pl = (currentPrice - position.buyPrice) * position.shares;
            const plPct = ((currentPrice - position.buyPrice) / position.buyPrice) * 100;

            return (
              <tr key={position.symbol}>
                <td>{position.symbol}</td>
                <td>{position.shares}</td>
                <td>{position.buyPrice.toLocaleString()}</td>
                <td>{currentPrice.toLocaleString()}</td>
                <td className={pl >= 0 ? 'profit' : 'loss'}>
                  {pl.toLocaleString()} ({plPct.toFixed(2)}%)
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
```

### Example 2: Market Sentiment Indicator

```python
import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta

def fetch_sentiment_trend(days=13):
    """Fetch sentiment trend for last N days"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    response = requests.get(
        'http://localhost:8000/api/v1/sentiment/trend',
        params={
            'start_date': str(start_date),
            'end_date': str(end_date),
            'interval': 'daily'
        }
    )
    return response.json()['data']['trend']

def create_sentiment_gauge(current_sentiment):
    """Create gauge chart for current sentiment"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=current_sentiment,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Market Sentiment"},
        gauge={
            'axis': {'range': [-1, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-1, -0.3], 'color': "rgba(239, 68, 68, 0.3)"},
                {'range': [-0.3, 0.3], 'color': "rgba(245, 158, 11, 0.3)"},
                {'range': [0.3, 1], 'color': "rgba(34, 197, 94, 0.3)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0
            }
        }
    ))
    return fig

# Streamlit App
st.title("📊 Market Sentiment Dashboard")

# Fetch data
trend_data = fetch_sentiment_trend()

# Current sentiment
current = trend_data[0]
st.metric(
    "Current Sentiment",
    f"{current['avg_sentiment']:.2f}",
    f"{current['article_count']} articles"
)

# Gauge chart
fig = create_sentiment_gauge(current['avg_sentiment'])
st.plotly_chart(fig)

# Trend chart
dates = [d['period'] for d in trend_data]
sentiments = [d['avg_sentiment'] for d in trend_data]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=dates,
    y=sentiments,
    mode='lines+markers',
    name='Sentiment',
    line=dict(color='rgb(34, 197, 94)', width=2)
))
fig.add_hline(y=0.3, line_dash="dash", line_color="green", annotation_text="Positive")
fig.add_hline(y=-0.3, line_dash="dash", line_color="red", annotation_text="Negative")
fig.update_layout(title="Sentiment Trend (13 days)")

st.plotly_chart(fig)

# Breakdown
st.subheader("Daily Breakdown")
for day in trend_data[:7]:  # Show last 7 days
    col1, col2, col3, col4 = st.columns(4)
    col1.write(day['period'])
    col2.metric("Sentiment", f"{day['avg_sentiment']:.2f}")
    col3.metric("Articles", day['article_count'])
    col4.write(f"👍 {day['positive_pct']:.1f}% | 👎 {day['negative_pct']:.1f}%")
```

---

## 🔧 Error Handling

### Common Errors

#### 400 Bad Request
```json
{
  "success": false,
  "detail": "Invalid date format. Use YYYY-MM-DD"
}
```

**Solution:** Check date format matches `YYYY-MM-DD`

#### 422 Validation Error
```json
{
  "success": false,
  "detail": [
    {
      "loc": ["query", "start_date"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Solution:** Provide all required parameters

#### 500 Internal Server Error
```json
{
  "success": false,
  "detail": "Query failed: ..."
}
```

**Solution:** Check date range is within available data (Oct 18-30, 2025)

### Error Handling Template

```typescript
async function apiCall<T>(
  url: string,
  params?: Record<string, string>
): Promise<T> {
  try {
    const queryString = params 
      ? '?' + new URLSearchParams(params).toString()
      : '';
    
    const response = await fetch(`${url}${queryString}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (!result.success) {
      throw new Error(result.detail || result.message || 'API request failed');
    }
    
    return result.data;
    
  } catch (error) {
    if (error instanceof Error) {
      console.error('API Error:', error.message);
      throw error;
    }
    throw new Error('Unknown error occurred');
  }
}

// Usage
try {
  const stocks = await apiCall<StockData[]>(
    'http://localhost:8000/api/v1/market/stocks',
    { start_date: '2025-10-25', end_date: '2025-10-30' }
  );
  console.log('Stocks:', stocks);
} catch (error) {
  // Handle error in UI
  showErrorNotification(error.message);
}
```

---

## 🚀 Best Practices

### 1. Caching
Cache API responses to reduce server load:

```javascript
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

async function cachedFetch(url, params) {
  const cacheKey = url + JSON.stringify(params);
  const cached = cache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  
  const response = await fetch(url + '?' + new URLSearchParams(params));
  const data = await response.json();
  
  cache.set(cacheKey, {
    data: data.data,
    timestamp: Date.now()
  });
  
  return data.data;
}
```

### 2. Batch Requests
Group multiple API calls:

```javascript
async function loadDashboardData(date) {
  const [stocks, sentiment, macro] = await Promise.all([
    fetch(`/api/v1/market/stocks?start_date=${date}&end_date=${date}`),
    fetch(`/api/v1/sentiment/summary?start_date=${date}&end_date=${date}`),
    fetch(`/api/v1/macro/forex?start_date=${date}&end_date=${date}`)
  ]);
  
  return {
    stocks: await stocks.json(),
    sentiment: await sentiment.json(),
    macro: await macro.json()
  };
}
```

### 3. Loading States
Always show loading indicators:

```tsx
function DataComponent() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch('...');
        const result = await response.json();
        setData(result.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!data) return <EmptyState />;

  return <DataDisplay data={data} />;
}
```

### 4. Date Range Validation
Validate dates before API calls:

```javascript
function isValidDateRange(startDate, endDate) {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const minDate = new Date('2025-10-18');
  const maxDate = new Date('2025-10-30');
  
  return start >= minDate && 
         end <= maxDate && 
         start <= end;
}

// Usage
if (!isValidDateRange(startDate, endDate)) {
  alert('Date range must be between Oct 18-30, 2025');
  return;
}
```

---

## 📞 Support

### Issues?
- Check date range is within Oct 18-30, 2025
- Verify all required parameters are provided
- Check response status and error messages
- Review examples in this documentation

### Test Endpoint
Always test with `/health` first:
```bash
curl http://localhost:8000/api/v1/health
```

### Response Times
Expected response times:
- Simple queries: 2-5s
- Market data (filtered): 5-8s
- Dashboard aggregations: 9-12s

If responses are slower, check:
- Network connection
- Backend server status
- Date range (smaller = faster)

---

## 📝 Changelog

### Version 1.0 (Oct 30, 2025)
- ✅ 13/14 endpoints working
- ✅ All TYPE_MISMATCH errors fixed
- ✅ Partition filtering implemented
- ✅ Dashboard correlation analysis working
- ⚠️ `/sentiment/articles` unavailable (Parquet schema issue)

---

**Status:** 🟢 Production Ready  
**Success Rate:** 92.9% (13/14 endpoints)  
**Avg Response Time:** 5-8 seconds  
**Data Available:** Oct 18-30, 2025 (13 days)

Happy coding! 🚀
    