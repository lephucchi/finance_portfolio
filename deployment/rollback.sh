#!/bin/bash

# =============================================================================
# Emergency Rollback Script
# =============================================================================
# Rollback to previous stable version in case of issues
# 
# Usage: ./deployment/rollback.sh [backup_directory]
# Example: ./deployment/rollback.sh ./backups/backup_20251025_120000
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BACKUP_DIR=$1

echo -e "${RED}===============================================================================${NC}"
echo -e "${RED}🔙 EMERGENCY ROLLBACK${NC}"
echo -e "${RED}===============================================================================${NC}"

# Check if backup directory is provided
if [ -z "$BACKUP_DIR" ]; then
    echo -e "${YELLOW}Available backups:${NC}"
    ls -lh ./backups/ 2>/dev/null || echo "No backups found"
    echo ""
    echo -e "${RED}Usage: ./deployment/rollback.sh [backup_directory]${NC}"
    echo -e "${YELLOW}Example: ./deployment/rollback.sh ./backups/backup_20251025_120000${NC}"
    exit 1
fi

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

echo -e "${YELLOW}Rollback Source: $BACKUP_DIR${NC}"
echo -e "${RED}⚠️  This will replace current deployment with backup${NC}"
echo -e "${YELLOW}Press Ctrl+C to cancel, or Enter to continue...${NC}"
read

# Stop current services
echo -e "\n${YELLOW}Stopping current services...${NC}"
docker-compose down

# Restore DAGs
echo -e "\n${YELLOW}Restoring DAGs from backup...${NC}"
if [ -d "$BACKUP_DIR/airflow/dags" ]; then
    rm -rf airflow/dags/*
    cp -r "$BACKUP_DIR/airflow/dags/"* airflow/dags/
    echo -e "${GREEN}✅ DAGs restored${NC}"
else
    echo -e "${RED}❌ No DAGs found in backup${NC}"
fi

# Restart services
echo -e "\n${YELLOW}Restarting services...${NC}"
docker-compose up -d

echo -e "\n${YELLOW}Waiting for services to start (60 seconds)...${NC}"
sleep 60

# Verify
echo -e "\n${YELLOW}Verifying rollback...${NC}"
docker-compose ps

echo -e "\n${GREEN}✅ Rollback completed${NC}"
echo -e "${YELLOW}Please verify system health:${NC}"
echo -e "  • Airflow UI: http://localhost:8080"
echo -e "  • Check DAGs: docker exec finance_portfolio-airflow-scheduler-1 airflow dags list"
echo -e "  • Monitor logs: docker-compose logs -f"
