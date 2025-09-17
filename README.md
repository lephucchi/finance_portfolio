# Finance Portfolio Research - End-to-End System

## Overview
This project builds a financial portfolio research platform using Databricks, FastAPI/NestJS, and Next.js.  
It integrates stock OHLCV data, financial reports, and news sentiment analysis to provide investors with insights via a web dashboard.

---

## Project Roadmap

### **Step 1. Data Source Integration**
- **Goal**: Collect stock data (OHLCV), financial reports, and news sentiment data.
- **Requirements**:
  - Connect to Vietstock API for OHLCV + financial reports.
  - Implement web scraping for financial news.
  - Store raw files in S3 (Raw Zone).
- **Tech Stack**: Python (requests, BeautifulSoup), Vietstock API, AWS S3.
- **Details**: Ensure structured ingestion (timestamped partitions). Apply retries + logging for data quality.

---

### **Step 2. Data Pipeline Orchestration**
- **Goal**: Automate ingestion, cleaning, and scheduling of data jobs.
- **Requirements**:
  - Set up Apache Airflow for orchestration.
  - Schedule daily OHLCV ingestion + weekly financial report updates.
  - Validate schema and handle missing values early.
- **Tech Stack**: Apache Airflow, Python, AWS S3.
- **Details**: DAGs manage workflows: ingestion → validation → store in S3.

---

### **Step 3. Databricks Lakehouse Setup**
- **Goal**: Transform raw data into a structured analytics-ready format.
- **Requirements**:
  - Mount S3 to Databricks workspace.
  - Create Delta Lake tables (Bronze → Silver → Gold).
  - Store cleaned OHLCV + enriched financial data.
- **Tech Stack**: Databricks, PySpark, Delta Lake.
- **Details**: Use Databricks notebooks for ETL, enforce schema evolution, and optimize Delta tables with Z-order indexing.

---

### **Step 4. Machine Learning Pipeline**
- **Goal**: Train ML models for trend prediction and sentiment scoring.
- **Requirements**:
  - Prepare features (technical indicators, sentiment embeddings).
  - Train models (LSTM, Transformer, PhoBERT for sentiment).
  - Register models in MLflow registry.
- **Tech Stack**: PyTorch, HuggingFace, MLflow, Databricks ML.
- **Details**: Store experiment runs in MLflow, monitor performance (MAE, R²).

---

### **Step 5. Analytics & Query Layer**
- **Goal**: Provide APIs to query processed data and ML predictions.
- **Requirements**:
  - Expose Databricks SQL endpoint for queries.
  - Backend connects to SQL endpoint for stock + sentiment insights.
- **Tech Stack**: Databricks SQL, FastAPI/NestJS, SQLAlchemy.
- **Details**: Secure with JWT-based authentication.

---

### **Step 6. Backend Service Development**
- **Goal**: Build API services to deliver insights to frontend.
- **Requirements**:
  - Data API: query historical OHLCV, KPIs, industry metrics.
  - AI API: return ML-based predictions (uptrend/downtrend, sentiment).
- **Tech Stack**: FastAPI (Python) or NestJS (TypeScript), Docker.
- **Details**: APIs connect to Databricks + MLflow registry.

---

### **Step 7. Frontend Dashboard**
- **Goal**: Provide visualization of data insights for end users.
- **Requirements**:
  - Build interactive dashboards: stock charts, heatmaps, portfolio insights.
  - Provide chatbot assistant for natural queries.
- **Tech Stack**: Next.js, TailwindCSS, Chart.js / Apache ECharts / Plotly (free alternative to TradingView).
- **Details**: Optimize for real-time updates with WebSocket (for live price data).

---

### **Step 8. CI/CD & Deployment**
- **Goal**: Automate build and deployment for production.
- **Requirements**:
  - Use GitHub Actions for CI/CD pipelines.
  - Deploy Frontend (Vercel), Backend (Railway/Render/Docker on EC2).
  - Secure S3 + Databricks credentials.
- **Tech Stack**: GitHub Actions, Docker, Vercel, Railway/Render.
- **Details**: Add monitoring (Grafana/Prometheus) for pipeline health.

---

## Deliverables
- End-to-end pipeline: ingestion → Databricks → ML → APIs → Dashboard.
- Documentation for setup and usage.
- CI/CD pipelines with production-ready deployment.

