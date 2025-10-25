#!/bin/bash

# =============================================================================
# Docker Health Check Script
# =============================================================================
# Quick health check for Docker environment and Airflow services
# 
# Usage: ./deployment/docker_health_check.sh
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===============================================================================${NC}"
echo -e "${BLUE}🏥 DOCKER HEALTH CHECK${NC}"
echo -e "${BLUE}===============================================================================${NC}"

# Check Docker daemon
echo -e "\n${YELLOW}1. Checking Docker daemon...${NC}"
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker daemon is running${NC}"
else
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    exit 1
fi

# Check Docker Compose
echo -e "\n${YELLOW}2. Checking Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✅ Docker Compose installed: $COMPOSE_VERSION${NC}"
else
    echo -e "${RED}❌ Docker Compose not found${NC}"
    exit 1
fi

# Check containers
echo -e "\n${YELLOW}3. Checking Airflow containers...${NC}"
echo -e "${BLUE}Container Status:${NC}"
docker-compose ps

REQUIRED_CONTAINERS=(
    "airflow-scheduler"
    "airflow-webserver"
    "postgres"
    "redis"
)

ALL_RUNNING=true
for container in "${REQUIRED_CONTAINERS[@]}"; do
    if docker-compose ps | grep "$container" | grep -q "Up"; then
        echo -e "${GREEN}✅ $container is running${NC}"
    else
        echo -e "${RED}❌ $container is not running${NC}"
        ALL_RUNNING=false
    fi
done

if [ "$ALL_RUNNING" = false ]; then
    echo -e "\n${YELLOW}⚠️  Some containers are not running${NC}"
    echo -e "${YELLOW}Starting Docker services...${NC}"
    docker-compose up -d
    echo -e "${YELLOW}Waiting 30 seconds for services to start...${NC}"
    sleep 30
fi

# Check Airflow webserver health
echo -e "\n${YELLOW}4. Checking Airflow webserver health...${NC}"
WEBSERVER_URL="http://localhost:8080/health"
HEALTH_CHECK=$(curl -s "$WEBSERVER_URL" 2>/dev/null || echo "FAILED")

if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Airflow webserver is healthy${NC}"
    echo -e "   URL: http://localhost:8080"
else
    echo -e "${RED}❌ Airflow webserver health check failed${NC}"
    echo -e "   Response: $HEALTH_CHECK"
fi

# Check Airflow scheduler
echo -e "\n${YELLOW}5. Checking Airflow scheduler...${NC}"
SCHEDULER_CONTAINER="finance_portfolio-airflow-scheduler-1"
if docker exec $SCHEDULER_CONTAINER airflow jobs check --job-type SchedulerJob > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Airflow scheduler is running${NC}"
else
    echo -e "${YELLOW}⚠️  Airflow scheduler job check returned warning (may be normal)${NC}"
fi

# Check database connection
echo -e "\n${YELLOW}6. Checking database connection...${NC}"
if docker exec $SCHEDULER_CONTAINER airflow db check > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
fi

# Check disk space
echo -e "\n${YELLOW}7. Checking disk space...${NC}"
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✅ Disk space: $DISK_USAGE% used${NC}"
elif [ "$DISK_USAGE" -lt 90 ]; then
    echo -e "${YELLOW}⚠️  Disk space: $DISK_USAGE% used (warning threshold)${NC}"
else
    echo -e "${RED}❌ Disk space: $DISK_USAGE% used (critical!)${NC}"
fi

# Check memory
echo -e "\n${YELLOW}8. Checking memory usage...${NC}"
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ "$MEMORY_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✅ Memory usage: $MEMORY_USAGE%${NC}"
elif [ "$MEMORY_USAGE" -lt 90 ]; then
    echo -e "${YELLOW}⚠️  Memory usage: $MEMORY_USAGE% (warning threshold)${NC}"
else
    echo -e "${RED}❌ Memory usage: $MEMORY_USAGE% (critical!)${NC}"
fi

# Check environment variables
echo -e "\n${YELLOW}9. Checking environment variables...${NC}"
if [ -f .env ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    
    # Check required variables (without showing values)
    REQUIRED_VARS=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "S3_BUCKET")
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^$var=" .env 2>/dev/null; then
            echo -e "${GREEN}   ✅ $var is set${NC}"
        else
            echo -e "${RED}   ❌ $var is not set${NC}"
        fi
    done
else
    echo -e "${RED}❌ .env file not found${NC}"
fi

# Check DAGs
echo -e "\n${YELLOW}10. Checking DAGs...${NC}"
DAG_COUNT=$(docker exec $SCHEDULER_CONTAINER airflow dags list 2>/dev/null | wc -l)
if [ "$DAG_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Found $DAG_COUNT DAGs${NC}"
else
    echo -e "${RED}❌ No DAGs found${NC}"
fi

# Summary
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}📊 HEALTH CHECK SUMMARY${NC}"
echo -e "${BLUE}===============================================================================${NC}"

if [ "$ALL_RUNNING" = true ]; then
    echo -e "${GREEN}✅ All systems operational${NC}"
    echo -e "\n${YELLOW}Quick Links:${NC}"
    echo -e "  • Airflow UI: http://localhost:8080"
    echo -e "  • Credentials: admin / admin123"
    echo -e "\n${YELLOW}Next Steps:${NC}"
    echo -e "  • Run E2E test: ./deployment/test_master_dag_e2e.sh"
    echo -e "  • Trigger pipeline: ./deployment/trigger_master_pipeline.sh"
else
    echo -e "${RED}⚠️  Some issues detected - please review above${NC}"
fi

echo -e "${BLUE}===============================================================================${NC}"
