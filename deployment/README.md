# Deployment Scripts - Finance Portfolio ETL Pipeline

This folder contains production deployment and testing scripts for the Finance Portfolio ETL Pipeline.

## 📋 Available Scripts

### 1. **test_master_dag_e2e.sh** - End-to-End Testing
Comprehensive end-to-end test for the entire master pipeline through Docker.

**Usage:**
```bash
./deployment/test_master_dag_e2e.sh
```

**What it tests:**
- ✅ Docker environment validation
- ✅ DAG import and structure validation
- ✅ All pipeline tasks (Bronze → Silver → Gold → RAG)
- ✅ Master pipeline coordination
- ✅ S3 data structure validation
- ✅ Production readiness checklist

**Output:**
- Creates detailed logs in `./test_logs/` directory
- Shows pass/fail status for each component
- Generates production readiness report

---

### 2. **trigger_master_pipeline.sh** - Production Pipeline Trigger
Triggers the master pipeline and monitors execution in real-time.

**Usage:**
```bash
# Trigger for today
./deployment/trigger_master_pipeline.sh

# Trigger for specific date
./deployment/trigger_master_pipeline.sh 2025-10-25
```

**Features:**
- 🚀 Triggers master_pipeline DAG
- 📊 Real-time execution monitoring
- ✅ Shows task states and progress
- 📝 Provides useful commands for debugging

---

### 3. **docker_health_check.sh** - Docker Environment Health
Quick health check for Docker environment and Airflow services.

**Usage:**
```bash
./deployment/docker_health_check.sh
```

---

### 4. **production_deploy.sh** - Production Deployment
Full production deployment with pre-checks and post-validation.

**Usage:**
```bash
./deployment/production_deploy.sh
```

---

### 5. **rollback.sh** - Emergency Rollback
Rollback to previous stable version in case of issues.

**Usage:**
```bash
./deployment/rollback.sh
```

---

## 🔧 Prerequisites

1. **Docker & Docker Compose installed**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Environment variables set**
   - Create `.env` file with:
   ```
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_DEFAULT_REGION=ap-southeast-1
   S3_BUCKET=bankanalystportfolio
   ```

3. **Docker services running**
   ```bash
   docker-compose up -d
   ```

---

## 📊 Testing Workflow

### Pre-Production Testing
```bash
# 1. Check Docker health
./deployment/docker_health_check.sh

# 2. Run comprehensive E2E test
./deployment/test_master_dag_e2e.sh

# 3. Review test logs
ls -lh ./test_logs/

# 4. If all tests pass, proceed to deployment
./deployment/production_deploy.sh
```

### Production Execution
```bash
# Trigger pipeline manually
./deployment/trigger_master_pipeline.sh

# Or let scheduler run automatically based on cron schedule
# master_pipeline: 6:00 AM weekdays
# bronze_layer: 6:00 AM weekdays
# silver_layer: 7:00 AM weekdays
# gold_layer: 8:00 AM weekdays
# rag_pipeline: 9:00 AM weekdays
```

---

## 🐛 Troubleshooting

### Container not running
```bash
docker-compose ps
docker-compose up -d
docker-compose logs -f airflow-scheduler
```

### DAG import errors
```bash
docker exec finance_portfolio-airflow-scheduler-1 airflow dags list-import-errors
```

### View task logs
```bash
docker exec finance_portfolio-airflow-scheduler-1 \
  airflow tasks log <dag_id> <task_id> <execution_date>
```

### Check S3 data
```bash
aws s3 ls s3://bankanalystportfolio/ --recursive | grep "$(date +%Y-%m-%d)"
```

---

## 📈 Monitoring

### Airflow Web UI
- URL: http://localhost:8080
- Username: admin
- Password: admin123 (or check `.env`)

### Check Pipeline Status
```bash
# DAG state
docker exec finance_portfolio-airflow-scheduler-1 \
  airflow dags state master_pipeline $(date +%Y-%m-%d)

# Task states
docker exec finance_portfolio-airflow-scheduler-1 \
  airflow tasks states-for-dag-run master_pipeline $(date +%Y-%m-%d)
```

---

## 🔐 Security Notes

- Never commit `.env` file with real credentials
- Use AWS IAM roles in production
- Rotate credentials regularly
- Monitor S3 access logs

---

## 📝 Change Log

### Version 2.0 (October 2025)
- ✅ Master DAG orchestration implemented
- ✅ Bronze → Silver → Gold → RAG pipeline
- ✅ Enhanced logging and metadata tracking
- ✅ Production-ready Docker deployment
- ✅ Comprehensive E2E testing

---

## 👥 Support

For issues or questions:
1. Check logs in `./test_logs/` and `./airflow/logs/`
2. Review documentation in `./docs/`
3. Contact: Banking Portfolio Team

---

**Last Updated:** October 25, 2025  
**Version:** 2.0 - Production Ready
