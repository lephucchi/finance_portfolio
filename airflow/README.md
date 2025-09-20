# Banking Portfolio Airflow Setup

Hướng dẫn setup và chạy Airflow cho Banking Portfolio Pipeline.

## 📋 Prerequisites

1. **Docker & Docker Compose** đã được cài đặt
2. **AWS credentials** đã được cấu hình
3. **S3 bucket** `bankanalystportfolio` đã tồn tại

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy environment file
cp .env.example .env

# Edit .env file với AWS credentials thật
nano .env
```

### 2. Start Airflow
```bash
# Initialize Airflow (first time only)
docker-compose up airflow-init

# Start all services
docker-compose up -d

# Check services status
docker-compose ps
```

### 3. Access Airflow Web UI
- URL: http://localhost:8080
- Username: admin
- Password: admin123

## 📊 DAG Overview

### 1. Master DAG (`master_dag`)
- **Schedule:** 6:00 AM weekdays
- **Purpose:** Orchestrate entire pipeline
- **Tasks:**
  - Check market status
  - Trigger sub-pipelines
  - Monitor execution
  - Generate daily reports

### 2. OHLCV DAG (`daily_stock_pipeline`)
- **Schedule:** 7:00 AM weekdays
- **Purpose:** Crawl banking stock data
- **Tasks:**
  - Crawl 27 banking stocks
  - Data validation
  - Health check

### 3. News DAG (`daily_news_pipeline`)
- **Schedule:** 8:00 AM weekdays
- **Purpose:** Crawl banking news
- **Tasks:**
  - Crawl from 4 news sources
  - Data validation
  - Sentiment analysis
  - Health check

## 🔧 Configuration

### Environment Variables
```bash
# Required AWS settings
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=ap-southeast-1

# Airflow settings
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin123
```

### Pipeline Settings
- **Retry Attempts:** 2
- **Timeout:** 4 hours
- **Execution:** Weekdays only
- **Parallel:** OHLCV và News run parallel

## 📁 Directory Structure
```
airflow/
├── dags/
│   ├── daily_stock_pipeline.py    # OHLCV DAG
│   ├── daily_news_pipeline.py     # News DAG
│   └── master_dag.py              # Master orchestrator
├── logs/                          # Airflow logs
├── plugins/                       # Custom plugins
└── config/                        # Additional configs
```

## 🛠️ Management Commands

### Start/Stop Services
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart airflow-scheduler
```

### View Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs airflow-scheduler
docker-compose logs airflow-webserver
```

### Maintenance
```bash
# Clean up old logs
docker-compose exec airflow-scheduler airflow db clean

# Reset database (careful!)
docker-compose down -v
docker-compose up airflow-init
```

## 📊 Monitoring

### Pipeline Status
1. **Web UI:** http://localhost:8080
2. **DAG View:** Check individual task status
3. **Graph View:** Visualize pipeline flow
4. **Logs:** Detailed execution logs

### S3 Monitoring
```bash
# Check OHLCV data
aws s3 ls s3://bankanalystportfolio/raw/ohlcv/date=2024-09-20/

# Check news data
aws s3 ls s3://bankanalystportfolio/raw/news/ --recursive

# Check logs
aws s3 ls s3://bankanalystportfolio/logs/ --recursive
```

## 🚨 Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER airflow/
   ```

2. **Memory Issues**
   ```bash
   # Increase Docker memory limit to 4GB+
   # Check Docker Desktop settings
   ```

3. **Port Conflicts**
   ```bash
   # Check if port 8080 is in use
   sudo netstat -tulpn | grep 8080
   ```

4. **Database Issues**
   ```bash
   # Reset database
   docker-compose down -v
   docker volume rm finance_portfolio_postgres-db-volume
   docker-compose up airflow-init
   ```

### Debug Mode
```bash
# Run with debug logs
docker-compose logs -f airflow-scheduler

# Execute DAG manually
docker-compose exec airflow-scheduler airflow dags trigger master_dag
```

## ⚡ Performance Tips

1. **Resource Allocation:**
   - CPU: 4+ cores recommended
   - RAM: 8GB+ recommended
   - Disk: 10GB+ free space

2. **Optimization:**
   - Monitor task execution times
   - Adjust timeout settings
   - Use appropriate retry policies

3. **Scaling:**
   - Consider CeleryExecutor for multiple workers
   - Implement task parallelization
   - Monitor resource usage

## 🔐 Security

1. **Environment Variables:**
   - Never commit `.env` file
   - Use strong passwords
   - Rotate AWS credentials regularly

2. **Network Security:**
   - Use VPN for production access
   - Implement IP whitelisting
   - Enable HTTPS in production

3. **Access Control:**
   - Use role-based access
   - Audit user activities
   - Regular security reviews