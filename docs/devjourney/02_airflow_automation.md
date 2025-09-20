# 📊 Day 02: Airflow Automation Setup

## 🎯 Objective
Tự động hóa Vietnamese Banking Portfolio Pipeline bằng Apache Airflow với Docker để schedule và monitor việc crawl OHLCV data và news data hàng ngày.

## 📋 Prerequisites Complete từ Day 01
- ✅ Python scripts hoạt động: `ingest_stock.py`, `ingest_news.py`
- ✅ Logging system integrated
- ✅ AWS S3 infrastructure ready
- ✅ 27 banking stocks OHLCV pipeline
- ✅ 4 major news sources pipeline

---

## 🐳 PART 1: DOCKER INFRASTRUCTURE SETUP

### 1. 🔧 Docker Installation
```bash
# Update system
sudo apt update

# Install Docker & Docker Compose
sudo apt install -y docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Verify installation
docker --version && docker-compose --version
```

**Results:**
- Docker version 27.5.1
- docker-compose version 1.29.2

### 2. 📁 Airflow Project Structure
```
airflow/
├── dags/
│   ├── daily_stock_pipeline.py   # OHLCV DAG
│   ├── daily_news_pipeline.py    # News DAG
│   └── master_dag.py             # Master orchestrator
├── logs/                         # Execution logs
├── plugins/                      # Custom plugins
├── config/                       # Configurations
└── README.md                     # Documentation
```

### 3. 🔧 Environment Configuration
Enhanced `.env` file với Airflow settings:
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_DEFAULT_REGION=ap-southeast-1
S3_BUCKET=bankanalystportfolio

# Airflow Configuration
AIRFLOW_UID=1000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin123
AIRFLOW_PROJ_DIR=.
PYTHONPATH=/opt/airflow/finance_portfolio

# Database
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
```

---

## ⚙️ PART 2: DOCKER COMPOSE SETUP

### 4. 🐋 Docker Compose Architecture
**Single docker-compose.yml** approach với:
- **PostgreSQL** as metadata database
- **Redis** for Celery backend
- **Airflow Webserver** (port 8080)
- **Airflow Scheduler** 
- **Airflow Triggerer** for async tasks

### 5. 🏗️ Services Configuration
```yaml
x-airflow-common: &airflow-common
  image: apache/airflow:2.7.1-python3.9
  environment:
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
    AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
    PYTHONPATH: '/opt/airflow/finance_portfolio'
  volumes:
    - ./airflow/dags:/opt/airflow/dags
    - ./airflow/logs:/opt/airflow/logs
    - .:/opt/airflow/finance_portfolio  # Mount entire project
```

### 6. 🔧 Challenges & Solutions

#### Problem 1: Import Errors
**Issue:** `ModuleNotFoundError: No module named 'airflow.operators.trigger_dag'`

**Solution:** Updated import trong `master_dag.py`:
```python
# ❌ Deprecated
from airflow.operators.trigger_dag import TriggerDagRunOperator

# ✅ Alternative solution
from airflow.operators.bash import BashOperator
trigger_task = BashOperator(
    bash_command='airflow dags trigger daily_stock_pipeline'
)
```

#### Problem 2: Permissions Issues
**Issue:** `PermissionError: [Errno 13] Permission denied: '/opt/airflow/logs/scheduler'`

**Solution:** 
```bash
# Fix permissions
sudo mkdir -p airflow/logs/scheduler
sudo chmod -R 777 airflow/
```

#### Problem 3: Initialization Complexity
**Issue:** Complex initialization script causing failures

**Solution:** Simplified `airflow-init` service:
```yaml
airflow-init:
  entrypoint: /entrypoint
  command:
    - bash
    - -c
    - |
      echo "🚀 Initializing Airflow..."
      mkdir -p /opt/airflow/logs/scheduler
      chmod -R 777 /opt/airflow/logs
      airflow db init
      airflow users create --username admin --password admin123 --role Admin
```

---

## 🔄 PART 3: DAG ARCHITECTURE

### 7. 📊 OHLCV DAG (`daily_stock_pipeline`)
**Schedule:** 7:00 AM weekdays  
**Purpose:** Crawl 27 banking stocks OHLCV data

**Tasks Flow:**
```
crawl_ohlcv_task → validate_data_task → health_check_task
```

**Key Features:**
- ✅ 27 banking stocks parallel processing
- ✅ Success rate monitoring (80% threshold)
- ✅ S3 validation
- ✅ Comprehensive error handling
- ✅ Logging integration

### 8. 📰 News DAG (`daily_news_pipeline`)  
**Schedule:** 8:00 AM weekdays  
**Purpose:** Crawl banking news từ 4 major sources

**Tasks Flow:**
```
crawl_news_task → validate_news_task → sentiment_analysis_task → health_check_task
```

**Key Features:**
- ✅ 4 major Vietnamese news sources
- ✅ Banking keyword filtering (100+ keywords)
- ✅ Sentiment analysis integration
- ✅ Source-wise statistics tracking
- ✅ S3 partitioned storage

### 9. 🎯 Master DAG (`master_dag`)
**Schedule:** 6:00 AM weekdays  
**Purpose:** Orchestrate entire pipeline

**Tasks Flow:**
```
init_orchestrator → check_market → [trigger_ohlcv, trigger_news] → 
[wait_ohlcv, wait_news] → monitor_pipelines → daily_report → final_health_check
```

**Key Features:**
- ✅ Market status validation (weekdays only)
- ✅ Parallel sub-pipeline execution
- ✅ Comprehensive monitoring
- ✅ Daily execution reports
- ✅ External task sensing

---

## 🚀 PART 4: DEPLOYMENT & TESTING

### 10. 🎯 Deployment Process
```bash
# 1. Initialize Airflow
sudo docker-compose up airflow-init

# 2. Start all services
sudo docker-compose up -d

# 3. Verify services
sudo docker-compose ps
```

**Results:**
```
SERVICE                 STATUS
postgres               Up (healthy)
redis                  Up (healthy)  
airflow-webserver      Up (healthy) - 0.0.0.0:8080->8080/tcp
airflow-scheduler      Up (healthy)
airflow-triggerer      Up (healthy)
```

### 11. ✅ Testing Results

#### DAG Loading Test
```bash
sudo docker exec airflow-scheduler airflow dags list
```
**Output:**
```
dag_id               | filepath                | owner            | paused
=====================+=========================+==================+=======
daily_news_pipeline  | daily_news_pipeline.py  | banking-portfolio| True
daily_stock_pipeline | daily_stock_pipeline.py | banking-portfolio| True  
master_dag           | master_dag.py           | banking-portfolio| True
```

#### Manual Trigger Tests
```bash
# Enable & trigger OHLCV DAG
sudo docker exec airflow-scheduler airflow dags unpause daily_stock_pipeline
sudo docker exec airflow-scheduler airflow dags trigger daily_stock_pipeline

# Enable & trigger News DAG  
sudo docker exec airflow-scheduler airflow dags unpause daily_news_pipeline
sudo docker exec airflow-scheduler airflow dags trigger daily_news_pipeline

# Enable & trigger Master DAG
sudo docker exec airflow-scheduler airflow dags unpause master_dag
sudo docker exec airflow-scheduler airflow dags trigger master_dag
```

**Results:** ✅ All DAGs successfully triggered and queued

### 12. 🌐 Web UI Access
- **URL:** http://localhost:8080
- **Username:** admin  
- **Password:** admin123
- **Health Check:** `curl -f http://localhost:8080/health`

**Status:** ✅ Web UI healthy và accessible

---

## 📊 PART 5: MONITORING & OPERATIONS

### 13. 📈 Pipeline Monitoring Features

#### Real-time Status Tracking
- **DAG States:** running, success, failed, queued
- **Task-level monitoring:** individual task success/failure
- **Execution duration tracking**
- **Retry mechanism monitoring**

#### Data Quality Validation
- **OHLCV Pipeline:** File count validation trên S3
- **News Pipeline:** Article count per source
- **Log File Validation:** Execution logs presence
- **Success Rate Monitoring:** 80% threshold cho OHLCV

#### Comprehensive Logging
- **Airflow Logs:** Task execution details
- **Application Logs:** S3-based structured logging
- **Performance Metrics:** Execution times, success rates
- **Error Tracking:** Detailed failure analysis

### 14. 🔧 Operational Commands

#### Service Management
```bash
# Check status
sudo docker-compose ps

# View logs
sudo docker-compose logs airflow-webserver
sudo docker-compose logs airflow-scheduler

# Restart services
sudo docker-compose restart airflow-scheduler

# Stop all services
sudo docker-compose down

# Start services
sudo docker-compose up -d
```

#### DAG Operations
```bash
# List DAGs
airflow dags list

# Check DAG runs
airflow dags list-runs -d daily_stock_pipeline

# Manual trigger
airflow dags trigger daily_stock_pipeline

# Pause/Unpause
airflow dags pause daily_stock_pipeline
airflow dags unpause daily_stock_pipeline
```

---

## 🎉 PART 6: ACHIEVEMENTS & RESULTS

### 15. ✅ Successfully Implemented

#### Infrastructure
- **Docker Environment:** Complete containerized setup
- **Database:** PostgreSQL metadata store
- **Web Interface:** Airflow UI accessible
- **Monitoring:** Real-time pipeline status

#### Pipeline Automation
- **3 Production DAGs:** OHLCV, News, Master orchestrator
- **Automated Scheduling:** Weekday execution 6-8 AM
- **Error Handling:** Comprehensive retry logic
- **Data Validation:** S3 file verification

#### Integration
- **Existing Scripts:** Seamless integration với Day 01 scripts
- **Logging System:** Enhanced logging với Airflow metadata
- **AWS S3:** Maintained S3 partition structure
- **Environment:** Proper credentials management

### 16. 📊 Pipeline Capabilities

#### OHLCV Data Pipeline
- **Coverage:** 27 Vietnamese banking stocks
- **Frequency:** Daily execution
- **Data Quality:** Complete OHLC validation
- **Storage:** Partitioned S3 structure
- **Monitoring:** Success rate tracking

#### News Data Pipeline  
- **Sources:** 4 major Vietnamese financial news
- **Processing:** Banking keyword filtering
- **Analysis:** Sentiment analysis integration
- **Storage:** Source-partitioned S3
- **Tracking:** Article count per source

#### Master Orchestration
- **Intelligence:** Market day detection
- **Coordination:** Parallel pipeline execution
- **Monitoring:** Comprehensive status tracking
- **Reporting:** Daily execution summaries

---

## 🚀 NEXT STEPS & FUTURE ENHANCEMENTS

### 17. 🔄 Immediate Improvements
- **Error Alerting:** Email/Slack notifications
- **Performance Optimization:** Task parallelization
- **Dependency Management:** Pip requirements in Docker
- **Resource Monitoring:** Memory và CPU usage tracking

### 18. 🌟 Advanced Features
- **Data Quality Rules:** Advanced validation logic
- **ML Pipeline Integration:** Automated model training
- **Dashboard Integration:** Real-time analytics
- **API Endpoints:** External system integration

### 19. 🔐 Production Readiness
- **Security:** HTTPS, authentication, access control
- **Scalability:** CeleryExecutor for multiple workers
- **Backup Strategy:** Database và logs backup
- **Disaster Recovery:** Multi-region deployment

---

## 📝 LESSONS LEARNED

### Technical Insights
1. **Single Docker Compose:** Simpler than multi-file approach
2. **Permission Management:** Critical for Docker volumes
3. **Import Compatibility:** Airflow version-specific imports
4. **Logging Strategy:** Centralized logging essential

### Best Practices Established  
1. **DAG Design:** Clear task dependencies
2. **Error Handling:** Comprehensive retry logic
3. **Monitoring:** Multi-level status tracking
4. **Documentation:** Complete setup guides

### Development Workflow
1. **Iterative Testing:** Manual trigger testing effective
2. **Modular Design:** Separate DAGs for separate concerns
3. **Environment Management:** Proper .env configuration
4. **Version Control:** All configurations in Git

---

## 🎯 SUCCESS METRICS

### Setup Completion ✅
- Docker environment: **100% operational**
- Airflow services: **All healthy**
- DAG loading: **3/3 successful**
- Web UI access: **Fully functional**

### Pipeline Testing ✅  
- OHLCV DAG: **Successfully triggered**
- News DAG: **Successfully triggered**
- Master DAG: **Successfully triggered**
- Monitoring: **Real-time status tracking**

### Integration Success ✅
- Day 01 scripts: **Fully integrated**
- AWS S3: **Maintained structure**
- Logging system: **Enhanced with Airflow**
- Environment: **Production-ready**

**🏆 Day 02 Result: Complete Airflow automation setup cho Vietnamese Banking Portfolio Pipeline!**