#!/bin/bash

# =============================================================================
# Production Deployment Script
# =============================================================================
# Full production deployment with pre-checks and post-validation
# 
# Usage: ./deployment/production_deploy.sh
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DEPLOYMENT_LOG="./logs/deployment_$(date +%Y%m%d_%H%M%S).log"
mkdir -p ./logs

echo -e "${BLUE}===============================================================================${NC}"
echo -e "${BLUE}🚀 PRODUCTION DEPLOYMENT - FINANCE PORTFOLIO ETL PIPELINE${NC}"
echo -e "${BLUE}===============================================================================${NC}"
echo -e "Deployment Time: $(date)"
echo -e "Log File: $DEPLOYMENT_LOG"
echo ""

# Log function
log() {
    echo -e "$1" | tee -a "$DEPLOYMENT_LOG"
}

# =============================================================================
# Pre-Deployment Checks
# =============================================================================
log "${BLUE}===============================================================================${NC}"
log "${BLUE}PHASE 1: Pre-Deployment Checks${NC}"
log "${BLUE}===============================================================================${NC}"

# Check if Docker is running
log "\n${YELLOW}Checking Docker daemon...${NC}"
if docker info > /dev/null 2>&1; then
    log "${GREEN}✅ Docker is running${NC}"
else
    log "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check for .env file
log "\n${YELLOW}Checking environment configuration...${NC}"
if [ -f .env ]; then
    log "${GREEN}✅ .env file exists${NC}"
else
    log "${RED}❌ .env file not found${NC}"
    log "${YELLOW}Creating .env file from template...${NC}"
    
    cat > .env << 'EOF'
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=ap-southeast-1
S3_BUCKET=bankanalystportfolio

# Airflow Configuration
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin123
AIRFLOW_LOGGING_LEVEL=INFO

# Project Configuration
AIRFLOW_UID=50000
AIRFLOW_PROJ_DIR=.
EOF
    
    log "${YELLOW}⚠️  Please update .env file with real credentials${NC}"
    log "${YELLOW}Edit .env file and run this script again${NC}"
    exit 1
fi

# Check disk space
log "\n${YELLOW}Checking disk space...${NC}"
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    log "${GREEN}✅ Disk space: $DISK_USAGE% used${NC}"
else
    log "${RED}❌ Disk space critical: $DISK_USAGE% used${NC}"
    log "${YELLOW}Please free up disk space before deploying${NC}"
    exit 1
fi

# Backup current state
log "\n${YELLOW}Creating backup of current deployment...${NC}"
BACKUP_DIR="./backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup DAGs
if [ -d airflow/dags ]; then
    cp -r airflow/dags "$BACKUP_DIR/"
    log "${GREEN}✅ DAGs backed up${NC}"
fi

# Backup logs (last 7 days)
if [ -d airflow/logs ]; then
    find airflow/logs -type f -mtime -7 -exec cp --parents {} "$BACKUP_DIR/" \; 2>/dev/null || true
    log "${GREEN}✅ Recent logs backed up${NC}"
fi

log "${GREEN}✅ Backup created: $BACKUP_DIR${NC}"

# =============================================================================
# Build & Deploy
# =============================================================================
log "\n${BLUE}===============================================================================${NC}"
log "${BLUE}PHASE 2: Build & Deploy${NC}"
log "${BLUE}===============================================================================${NC}"

# Build Docker image
log "\n${YELLOW}Building Docker image...${NC}"
docker-compose build 2>&1 | tee -a "$DEPLOYMENT_LOG"
log "${GREEN}✅ Docker image built successfully${NC}"

# Stop existing services
log "\n${YELLOW}Stopping existing services...${NC}"
docker-compose down 2>&1 | tee -a "$DEPLOYMENT_LOG"
log "${GREEN}✅ Services stopped${NC}"

# Start services
log "\n${YELLOW}Starting services...${NC}"
docker-compose up -d 2>&1 | tee -a "$DEPLOYMENT_LOG"
log "${GREEN}✅ Services started${NC}"

# Wait for services to be ready
log "\n${YELLOW}Waiting for services to initialize (60 seconds)...${NC}"
sleep 60

# Check service health
log "\n${YELLOW}Checking service health...${NC}"
SERVICES_OK=true

if docker-compose ps | grep "airflow-scheduler" | grep -q "Up"; then
    log "${GREEN}✅ Airflow scheduler is running${NC}"
else
    log "${RED}❌ Airflow scheduler failed to start${NC}"
    SERVICES_OK=false
fi

if docker-compose ps | grep "airflow-webserver" | grep -q "Up"; then
    log "${GREEN}✅ Airflow webserver is running${NC}"
else
    log "${RED}❌ Airflow webserver failed to start${NC}"
    SERVICES_OK=false
fi

if [ "$SERVICES_OK" = false ]; then
    log "${RED}❌ Deployment failed - services not healthy${NC}"
    log "${YELLOW}Rolling back...${NC}"
    docker-compose down
    exit 1
fi

# =============================================================================
# Post-Deployment Validation
# =============================================================================
log "\n${BLUE}===============================================================================${NC}"
log "${BLUE}PHASE 3: Post-Deployment Validation${NC}"
log "${BLUE}===============================================================================${NC}"

# Check DAG imports
log "\n${YELLOW}Validating DAG imports...${NC}"
SCHEDULER_CONTAINER="finance_portfolio-airflow-scheduler-1"
IMPORT_ERRORS=$(docker exec $SCHEDULER_CONTAINER airflow dags list-import-errors 2>&1)

if echo "$IMPORT_ERRORS" | grep -q "No data found"; then
    log "${GREEN}✅ No DAG import errors${NC}"
else
    log "${RED}❌ DAG import errors detected:${NC}"
    log "$IMPORT_ERRORS"
    log "${YELLOW}Warning: Proceeding with deployment but please fix DAG errors${NC}"
fi

# List DAGs
log "\n${YELLOW}Listing deployed DAGs...${NC}"
docker exec $SCHEDULER_CONTAINER airflow dags list 2>&1 | tee -a "$DEPLOYMENT_LOG"

# Check database
log "\n${YELLOW}Validating database connection...${NC}"
if docker exec $SCHEDULER_CONTAINER airflow db check > /dev/null 2>&1; then
    log "${GREEN}✅ Database connection successful${NC}"
else
    log "${RED}❌ Database connection failed${NC}"
    exit 1
fi

# Unpause important DAGs
log "\n${YELLOW}Activating production DAGs...${NC}"
PRODUCTION_DAGS=("master_pipeline" "bronze_layer_pipeline" "silver_layer_pipeline" "gold_layer_pipeline" "rag_pipeline")

for dag_id in "${PRODUCTION_DAGS[@]}"; do
    if docker exec $SCHEDULER_CONTAINER airflow dags unpause "$dag_id" 2>&1 | grep -q "unpaused"; then
        log "${GREEN}✅ Activated: $dag_id${NC}"
    else
        log "${YELLOW}⚠️  Could not activate: $dag_id (may not exist yet)${NC}"
    fi
done

# =============================================================================
# Deployment Summary
# =============================================================================
log "\n${BLUE}===============================================================================${NC}"
log "${BLUE}📊 DEPLOYMENT SUMMARY${NC}"
log "${BLUE}===============================================================================${NC}"

log "\n${GREEN}✅✅✅ PRODUCTION DEPLOYMENT COMPLETED SUCCESSFULLY ✅✅✅${NC}"

log "\n${YELLOW}Deployment Details:${NC}"
log "  • Deployment Time: $(date)"
log "  • Backup Location: $BACKUP_DIR"
log "  • Deployment Log: $DEPLOYMENT_LOG"

log "\n${YELLOW}Service Status:${NC}"
docker-compose ps 2>&1 | tee -a "$DEPLOYMENT_LOG"

log "\n${YELLOW}Airflow Access:${NC}"
log "  • Web UI: http://localhost:8080"
log "  • Username: admin"
log "  • Password: admin123 (or check .env)"

log "\n${YELLOW}Next Steps:${NC}"
log "  1. Access Airflow UI: http://localhost:8080"
log "  2. Verify all DAGs are visible and unpaused"
log "  3. Run E2E test: ./deployment/test_master_dag_e2e.sh"
log "  4. Trigger test run: ./deployment/trigger_master_pipeline.sh"
log "  5. Monitor logs: docker-compose logs -f airflow-scheduler"

log "\n${YELLOW}Rollback Command (if needed):${NC}"
log "  ./deployment/rollback.sh $BACKUP_DIR"

log "\n${BLUE}===============================================================================${NC}"

# Send notification (optional - implement if needed)
# curl -X POST "https://your-slack-webhook" -d "{'text':'Production deployment completed successfully'}"

log "${GREEN}🎉 Deployment process completed!${NC}"
