#!/bin/bash

# =============================================================================
# System Monitoring Script
# =============================================================================
# This script monitors the health and performance of Finance Portfolio
# Run as: bash monitor.sh
# Or add to crontab: */5 * * * * /home/ubuntu/finance_portfolio/deployment/monitor.sh
# =============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
LOG_FILE="/home/ubuntu/finance_portfolio/logs/monitor.log"
ALERT_EMAIL="admin@example.com"
PROJECT_DIR="/home/ubuntu/finance_portfolio"

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# =============================================================================
# Helper Functions
# =============================================================================

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

check_service() {
    local service_name=$1
    local url=$2
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ $service_name: UP (HTTP $http_code)${NC}"
        log "✅ $service_name: UP"
        return 0
    else
        echo -e "${RED}❌ $service_name: DOWN (HTTP $http_code)${NC}"
        log "❌ $service_name: DOWN (HTTP $http_code)"
        return 1
    fi
}

# =============================================================================
# Health Checks
# =============================================================================

echo -e "\n${GREEN}=== Finance Portfolio Health Check ===${NC}"
echo "Time: $TIMESTAMP"
echo ""

# Backend API
check_service "Backend API" "http://localhost:8000/health"
BACKEND_STATUS=$?

# Frontend
check_service "Frontend" "http://localhost:5173"
FRONTEND_STATUS=$?

# Airflow Webserver
check_service "Airflow Web" "http://localhost:8080/health"
AIRFLOW_STATUS=$?

# =============================================================================
# Docker Container Status
# =============================================================================

echo -e "\n${GREEN}=== Docker Containers ===${NC}"
cd "$PROJECT_DIR"
docker-compose ps

# Count running containers
RUNNING=$(docker-compose ps | grep "Up" | wc -l)
TOTAL=$(docker-compose ps | tail -n +3 | wc -l)

if [ "$RUNNING" -eq "$TOTAL" ]; then
    echo -e "${GREEN}✅ All containers running ($RUNNING/$TOTAL)${NC}"
    log "✅ All containers running ($RUNNING/$TOTAL)"
else
    echo -e "${YELLOW}⚠️  Some containers down ($RUNNING/$TOTAL)${NC}"
    log "⚠️  Some containers down ($RUNNING/$TOTAL)"
fi

# =============================================================================
# System Resources
# =============================================================================

echo -e "\n${GREEN}=== System Resources ===${NC}"

# CPU Usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo "CPU Usage: ${CPU_USAGE}%"
log "CPU Usage: ${CPU_USAGE}%"

if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo -e "${RED}⚠️  High CPU usage!${NC}"
    log "⚠️  High CPU usage!"
fi

# Memory Usage
MEMORY=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
echo "Memory Usage: ${MEMORY}%"
log "Memory Usage: ${MEMORY}%"

if (( $(echo "$MEMORY > 85" | bc -l) )); then
    echo -e "${RED}⚠️  High memory usage!${NC}"
    log "⚠️  High memory usage!"
fi

# Disk Usage
DISK=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
echo "Disk Usage: ${DISK}%"
log "Disk Usage: ${DISK}%"

if [ "$DISK" -gt 85 ]; then
    echo -e "${RED}⚠️  High disk usage!${NC}"
    log "⚠️  High disk usage!"
fi

# =============================================================================
# Docker Stats
# =============================================================================

echo -e "\n${GREEN}=== Docker Resource Usage ===${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# =============================================================================
# Database Status
# =============================================================================

echo -e "\n${GREEN}=== Database Status ===${NC}"
cd "$PROJECT_DIR"

# Check PostgreSQL
POSTGRES_STATUS=$(docker-compose exec -T postgres pg_isready -U airflow 2>&1)
if echo "$POSTGRES_STATUS" | grep -q "accepting connections"; then
    echo -e "${GREEN}✅ PostgreSQL: UP${NC}"
    log "✅ PostgreSQL: UP"
else
    echo -e "${RED}❌ PostgreSQL: DOWN${NC}"
    log "❌ PostgreSQL: DOWN"
fi

# Database size
DB_SIZE=$(docker-compose exec -T postgres psql -U airflow -t -c "SELECT pg_size_pretty(pg_database_size('airflow'));" 2>/dev/null | xargs)
echo "Database Size: $DB_SIZE"
log "Database Size: $DB_SIZE"

# =============================================================================
# Log File Sizes
# =============================================================================

echo -e "\n${GREEN}=== Log File Sizes ===${NC}"
du -sh "$PROJECT_DIR/web_executor/backend/logs" 2>/dev/null || echo "Backend logs: N/A"
du -sh "$PROJECT_DIR/airflow/logs" 2>/dev/null || echo "Airflow logs: N/A"

# =============================================================================
# Network Connectivity
# =============================================================================

echo -e "\n${GREEN}=== Network Connectivity ===${NC}"

# AWS S3
if aws s3 ls s3://bankanalystportfolio/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ AWS S3: Connected${NC}"
    log "✅ AWS S3: Connected"
else
    echo -e "${RED}❌ AWS S3: Connection failed${NC}"
    log "❌ AWS S3: Connection failed"
fi

# =============================================================================
# Recent Errors
# =============================================================================

echo -e "\n${GREEN}=== Recent Errors (last 10) ===${NC}"

# Backend errors
echo "Backend errors:"
docker-compose logs --tail=100 backend 2>/dev/null | grep -i error | tail -5 || echo "No recent errors"

# Airflow errors
echo -e "\nAirflow errors:"
docker-compose logs --tail=100 airflow-scheduler 2>/dev/null | grep -i error | tail -5 || echo "No recent errors"

# =============================================================================
# Summary
# =============================================================================

echo -e "\n${GREEN}=== Summary ===${NC}"

ISSUES=0

if [ $BACKEND_STATUS -ne 0 ]; then ((ISSUES++)); fi
if [ $FRONTEND_STATUS -ne 0 ]; then ((ISSUES++)); fi
if [ $AIRFLOW_STATUS -ne 0 ]; then ((ISSUES++)); fi

if [ "$ISSUES" -eq 0 ]; then
    echo -e "${GREEN}✅ All systems operational${NC}"
    log "✅ All systems operational"
else
    echo -e "${RED}❌ $ISSUES issues detected${NC}"
    log "❌ $ISSUES issues detected"
fi

echo -e "\nMonitoring log: $LOG_FILE"
echo "Last updated: $TIMESTAMP"
