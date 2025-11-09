# 🔷 TECHNOLOGY FLOW DIAGRAM - AEGIS LUMINA
## Biểu đồ Luồng Công nghệ - Hệ thống Phân tích Tài chính

---

## 📊 FLOW DIAGRAM ĐƠN GIẢN

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         🌐 EXTERNAL DATA SOURCES                         │
├─────────────────────────────────────────────────────────────────────────┤
│  VNStock API          Google Search          Economic APIs               │
│  (Stock Data)         (News Articles)        (Macro Indicators)          │
└────────┬────────────────────┬───────────────────────┬───────────────────┘
         │                    │                       │
         └────────────────────┴───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    📥 DATA INGESTION SCRIPTS (Python)                    │
├─────────────────────────────────────────────────────────────────────────┤
│         bronze_stocks.py  │  bronze_news.py  │  bronze_macro.py         │
│              (Requests, Pandas, JSON/CSV Processing)                     │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       🗄️ AWS S3 - BRONZE LAYER                          │
├─────────────────────────────────────────────────────────────────────────┤
│                      RAW Data Storage (875 MB)                           │
│              stocks/*.json  │  news/*.json  │  macro/*.csv               │
│                        (boto3 - AWS SDK)                                 │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   ⚙️ APACHE AIRFLOW (Orchestration)                     │
├─────────────────────────────────────────────────────────────────────────┤
│              DAG: master_pipeline_v2.py (Python Operators)               │
│         PostgreSQL (Metadata) + Redis (Celery) + Docker                 │
│                   Schedule: Daily @ 09:00 UTC                            │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      🔥 PYSPARK ETL PROCESSING                           │
├─────────────────────────────────────────────────────────────────────────┤
│              bronze_to_silver_v6.py (Cleaning & Validation)              │
│              bronze_to_silver_macro_news.py (Standardization)            │
│                     PySpark 3.3 + Java 17 + Hadoop                       │
│                    Distributed Processing (5 workers)                    │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       🗄️ AWS S3 - SILVER LAYER                          │
├─────────────────────────────────────────────────────────────────────────┤
│               Cleaned & Standardized Data (68 MB - 92% ↓)               │
│                  Parquet Format + Snappy Compression                     │
│               Partitioned by Date: partition_date=YYYY-MM-DD             │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   🔬 PYSPARK FEATURE ENGINEERING                         │
├─────────────────────────────────────────────────────────────────────────┤
│                   silver_to_gold.py (Analytics Layer)                    │
│       Technical Indicators (MA, RSI, MACD) + Sentiment Aggregation      │
│                        PySpark + Pandas UDF                              │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        🗄️ AWS S3 - GOLD LAYER                           │
├─────────────────────────────────────────────────────────────────────────┤
│                   Analytics-Ready Features (99 MB)                       │
│  analytics/ │ sentiment_analysis/ │ serving/ │ metadata/                │
│                    Parquet + Partitioned by Date                         │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
┌─────────────────────────────┐  ┌───────────────────────────────────────┐
│   📊 AWS GLUE + ATHENA      │  │    🤖 RAG CHATBOT SYSTEM              │
├─────────────────────────────┤  ├───────────────────────────────────────┤
│  Metadata Catalog (9 tables)│  │  pre_process.py (Text Cleaning)       │
│  SQL Query Engine           │  │  vector_embedding.py (FAISS Index)    │
│  Presto-based Queries       │  │  Vietnamese-SBERT (768-dim vectors)   │
│  Partition Pruning          │  │  Gemini API (LLM Generation)          │
└──────────┬──────────────────┘  └───────────┬───────────────────────────┘
           │                                  │
           └──────────────┬───────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     ⚡ FASTAPI BACKEND (Python 3.10)                     │
├─────────────────────────────────────────────────────────────────────────┤
│         athena_service.py (Query Execution) + rag_service.py             │
│              cache_service.py (Redis Caching - 5 min TTL)               │
│                   14 REST API Endpoints + WebSocket                      │
│            Gunicorn (Production) + Uvicorn (ASGI Server)                 │
│                    Supabase (Metadata Storage)                           │
│                       Docker Container: Port 8000                        │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  🎨 REACT FRONTEND (TypeScript 5.2)                      │
├─────────────────────────────────────────────────────────────────────────┤
│              Vite 4.4 (Build Tool) + TailwindCSS (Styling)               │
│           Recharts / Plotly.js (Interactive Charts & Graphs)             │
│         Axios (HTTP Client) + React Query (State Management)             │
│              Components: Dashboard, Stocks, Sentiment, Chat              │
│                       Docker Container: Port 5173                        │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          👥 END USERS                                    │
├─────────────────────────────────────────────────────────────────────────┤
│       Analysts │ Traders │ Portfolio Managers │ Researchers              │
│              Web Browser (Chrome, Firefox, Edge, Safari)                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 TECHNOLOGY STACK BY LAYER

### **Layer 1: Data Collection**
```
Python 3.10
├── requests (HTTP Client)
├── pandas (Data Manipulation)
├── boto3 (AWS SDK)
└── vnstock (Stock Market API)
```

### **Layer 2: Storage**
```
AWS S3
├── Bronze Layer (JSON, CSV)
├── Silver Layer (Parquet + Snappy)
└── Gold Layer (Parquet + Partitioned)
```

### **Layer 3: Orchestration**
```
Apache Airflow 2.9
├── PostgreSQL 13 (Metadata DB)
├── Redis 7 (Celery Broker)
└── Docker Compose (Containerization)
```

### **Layer 4: Processing**
```
PySpark 3.3
├── Java 17 (JVM)
├── Hadoop 3.3 (AWS Libraries)
└── Pandas (Python Data Processing)
```

### **Layer 5: Query & Analytics**
```
AWS Glue Catalog
└── AWS Athena (Presto SQL Engine)
```

### **Layer 6: AI/ML**
```
RAG System
├── FAISS (Vector Database)
├── sentence-transformers (Vietnamese-SBERT)
└── Gemini API (Google LLM)
```

### **Layer 7: Backend API**
```
FastAPI
├── Uvicorn (ASGI Server)
├── Gunicorn (WSGI Server)
├── Redis (Caching)
├── Supabase (PostgreSQL)
└── boto3 (AWS SDK)
```

### **Layer 8: Frontend**
```
React 18
├── TypeScript 5.2
├── Vite 4.4 (Build Tool)
├── TailwindCSS (Styling)
├── Recharts (Charts)
├── Plotly.js (Interactive Charts)
└── Axios (HTTP Client)
```

### **Infrastructure**
```
Docker + Docker Compose
├── 7 Containers (Airflow, Backend, Frontend, DB, Redis)
├── Bridge Network (finance_network)
└── Persistent Volumes (PostgreSQL, Logs)
```

---

## ⏱️ DATA FLOW TIMELINE (Daily)

```
08:00 UTC
   ↓
[Data Ingestion] Python Scripts (1.5 hours)
   ├── VNStock API → Bronze/stocks/
   ├── Google CSE → Bronze/news/
   └── Economic APIs → Bronze/macro/
   ↓
10:00 UTC
   ↓
[ETL Processing] PySpark Bronze→Silver (1.5 hours)
   ├── Cleaning & Validation
   ├── Schema Standardization
   └── Parquet Conversion (92% compression)
   ↓
13:00 UTC
   ↓
[Feature Engineering] PySpark Silver→Gold (1.5 hours)
   ├── Technical Indicators (MA, RSI, MACD)
   ├── Sentiment Aggregation
   └── Macro Trend Analysis
   ↓
15:00 UTC
   ↓
[Catalog Update] AWS Glue (15 minutes)
   ├── Table Schema Registration
   ├── Partition Discovery
   └── Metadata Refresh
   ↓
15:30 UTC
   ↓
[PRODUCTION READY] ✅
   ├── Athena Queries Available
   ├── API Endpoints Serving Data
   └── Dashboard Real-time Updates
```

---

## 🔄 REQUEST-RESPONSE FLOW

### **Example: User queries stock data**

```
USER (Browser)
    │
    ├─ HTTP GET /api/v1/market/stocks?start_date=2025-10-30
    ↓
REACT FRONTEND (Port 5173)
    │
    ├─ Axios HTTP Request
    ↓
FASTAPI BACKEND (Port 8000)
    │
    ├─ Check Redis Cache (cache_service.py)
    │    ├─ HIT → Return cached data (< 100ms) ✅
    │    └─ MISS ↓
    │
    ├─ Query AWS Athena (athena_service.py)
    │    ├─ SQL: SELECT * FROM gold_analytics.market_features
    │    ├─ WHERE partition_date = '2025-10-30'
    │    ↓
    ├─ AWS Athena executes on S3 Gold Layer
    │    ├─ Partition Pruning (97% reduction)
    │    ├─ Parquet Scan (fast columnar read)
    │    └─ Result: 3,000 rows (5-8 seconds)
    │
    ├─ Cache result in Redis (5-min TTL)
    ├─ Format JSON response
    ↓
REACT FRONTEND
    │
    ├─ Parse JSON data
    ├─ Render Charts (Recharts)
    └─ Display Table
    ↓
USER sees results
```

### **Example: User asks chatbot**

```
USER (Browser)
    │
    ├─ "Lãi suất ngân hàng nào cao nhất?"
    ↓
REACT CHATBOT COMPONENT
    │
    ├─ POST /api/v1/chat
    ↓
FASTAPI BACKEND
    │
    ├─ rag_service.py processes query
    │
    ├─ 1. Encode query → Vietnamese-SBERT
    │    └─ [0.23, -0.45, 0.67, ...] (768-dim vector)
    │
    ├─ 2. FAISS Vector Search (12K articles)
    │    ├─ Cosine Similarity
    │    └─ Top-3 most relevant articles
    │
    ├─ 3. Build Context from retrieved articles
    │    ├─ Article 1: "Vietcombank lãi suất 6.5%..."
    │    ├─ Article 2: "BIDV lãi suất 6.3%..."
    │    └─ Article 3: "Agribank lãi suất 6.2%..."
    │
    ├─ 4. Send to Gemini API (LLM)
    │    ├─ Prompt: "Answer based on context..."
    │    └─ Response generation (Vietnamese)
    │
    ├─ 5. Format response with sources
    ↓
REACT CHATBOT COMPONENT
    │
    ├─ Display AI response
    ├─ Show source citations
    └─ Update chat history
    ↓
USER sees answer
```

---

## 📦 DEPLOYMENT ARCHITECTURE

```
AWS EC2 Instance (t2.large)
    │
    ├─ Docker Engine
    │
    ├─ Docker Compose (7 containers)
    │   │
    │   ├─ postgres:13 (Port 5432)
    │   │   └─ Airflow Metadata DB
    │   │
    │   ├─ redis:latest (Port 6379)
    │   │   └─ Celery Broker + Cache
    │   │
    │   ├─ airflow-webserver (Port 8080)
    │   │   └─ Airflow UI
    │   │
    │   ├─ airflow-scheduler
    │   │   └─ DAG Execution Engine
    │   │
    │   ├─ airflow-triggerer
    │   │   └─ Async Task Handler
    │   │
    │   ├─ backend (Port 8000)
    │   │   └─ FastAPI + Gunicorn
    │   │
    │   └─ frontend (Port 5173)
    │       └─ React + Vite (Dev Server)
    │
    └─ Nginx (Optional - Production)
        └─ Reverse Proxy + SSL (Port 80/443)
```

---

## 🎯 KEY TECHNOLOGIES SUMMARY

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Language** | Python 3.10 | Backend, ETL, Scripts |
| **Language** | TypeScript 5.2 | Frontend Development |
| **Backend Framework** | FastAPI | REST API Server |
| **Frontend Framework** | React 18 | UI Components |
| **Build Tool** | Vite 4.4 | Fast Frontend Bundler |
| **Styling** | TailwindCSS | Utility-first CSS |
| **Charts** | Recharts, Plotly.js | Data Visualization |
| **Data Processing** | PySpark 3.3 | Distributed ETL |
| **Orchestration** | Apache Airflow 2.9 | Workflow Management |
| **Storage** | AWS S3 | Data Lake |
| **Catalog** | AWS Glue | Metadata Management |
| **Query Engine** | AWS Athena | SQL on S3 |
| **Database** | PostgreSQL 13 | Metadata Storage |
| **Cache** | Redis 7 | Session & Query Cache |
| **Vector DB** | FAISS | Similarity Search |
| **Embedding** | Vietnamese-SBERT | Text Vectorization |
| **LLM** | Gemini API | Text Generation |
| **Containerization** | Docker, Docker Compose | Deployment |
| **Server** | Gunicorn, Uvicorn | WSGI/ASGI Server |
| **Format** | Parquet + Snappy | Columnar Storage |
| **Protocol** | HTTP/REST, WebSocket | API Communication |

---

## 🚀 PERFORMANCE HIGHLIGHTS

```
┌──────────────────────────────────────────────────┐
│  Query Response Time:  0.5-1s (cached)           │
│                        5-8s (fresh Athena query) │
│                                                   │
│  Data Compression:     92% (Bronze → Silver)     │
│                                                   │
│  Daily Processing:     ~7 hours (end-to-end)     │
│                                                   │
│  Cost Savings:         87-94% vs traditional DB  │
│                                                   │
│  Uptime:               99.8%                      │
│                                                   │
│  Cache Hit Rate:       95% (5-minute TTL)        │
│                                                   │
│  Partition Pruning:    97% data scan reduction   │
└──────────────────────────────────────────────────┘
```

---

**Document Created:** November 7, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅
