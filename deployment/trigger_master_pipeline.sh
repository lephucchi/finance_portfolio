#!/bin/bash

# =============================================================================
# Trigger Master Pipeline - Production Execution
# =============================================================================
# This script triggers the master_pipeline DAG and monitors its execution
# 
# Usage: ./scripts/trigger_master_pipeline.sh [execution_date]
# Example: ./scripts/trigger_master_pipeline.sh 2025-10-25
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

AIRFLOW_CONTAINER="finance_portfolio-airflow-scheduler-1"
EXECUTION_DATE=${1:-$(date +%Y-%m-%d)}
LOG_FILE="./logs/master_pipeline_execution_$(date +%Y%m%d_%H%M%S).log"

mkdir -p ./logs

echo -e "${BLUE}===============================================================================${NC}"
echo -e "${BLUE}🚀 TRIGGERING MASTER PIPELINE - PRODUCTION EXECUTION${NC}"
echo -e "${BLUE}===============================================================================${NC}"
echo -e "Execution Date: ${EXECUTION_DATE}"
echo -e "Log File: ${LOG_FILE}"
echo ""

# Check if Docker container is running
echo -e "${YELLOW}Checking Docker environment...${NC}"
if ! docker ps | grep -q "$AIRFLOW_CONTAINER"; then
    echo -e "${RED}❌ Airflow scheduler is not running${NC}"
    echo -e "${YELLOW}Please start Docker services: docker-compose up -d${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker environment is ready${NC}"

# Unpause DAG if paused
echo -e "\n${YELLOW}Ensuring DAG is unpaused...${NC}"
docker exec $AIRFLOW_CONTAINER airflow dags unpause master_pipeline
echo -e "${GREEN}✅ DAG is active${NC}"

# Trigger the DAG
echo -e "\n${YELLOW}Triggering master_pipeline...${NC}"
RUN_ID=$(docker exec $AIRFLOW_CONTAINER airflow dags trigger master_pipeline --exec-date "$EXECUTION_DATE" 2>&1 | grep "Created" | awk '{print $NF}' || echo "manual__$(date +%Y-%m-%dT%H:%M:%S)+00:00")

echo -e "${GREEN}✅ Pipeline triggered successfully${NC}"
echo -e "Run ID: ${RUN_ID}"

# Monitor execution
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}📊 MONITORING PIPELINE EXECUTION${NC}"
echo -e "${BLUE}===============================================================================${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop monitoring (pipeline will continue running)${NC}\n"

# Function to get DAG run state
get_dag_state() {
    docker exec $AIRFLOW_CONTAINER airflow dags state master_pipeline "$EXECUTION_DATE" 2>/dev/null || echo "unknown"
}

# Function to get task states
get_task_states() {
    docker exec $AIRFLOW_CONTAINER airflow tasks states-for-dag-run master_pipeline "$EXECUTION_DATE" 2>/dev/null || echo "No task states available"
}

# Monitor loop
ITERATION=0
MAX_ITERATIONS=120  # 120 * 30 seconds = 1 hour max monitoring

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    
    # Clear screen for cleaner output
    clear
    
    echo -e "${BLUE}===============================================================================${NC}"
    echo -e "${BLUE}📊 PIPELINE EXECUTION STATUS (Iteration $ITERATION/$MAX_ITERATIONS)${NC}"
    echo -e "${BLUE}===============================================================================${NC}"
    echo -e "Execution Date: ${EXECUTION_DATE}"
    echo -e "Time: $(date +%Y-%m-%d\ %H:%M:%S)"
    echo ""
    
    # Get overall DAG state
    DAG_STATE=$(get_dag_state)
    echo -e "Overall State: ${YELLOW}$DAG_STATE${NC}"
    echo ""
    
    # Get task states
    echo -e "${YELLOW}Task States:${NC}"
    echo -e "$(get_task_states)" | grep -E "success|running|failed|upstream_failed|skipped" || echo "  Waiting for tasks to start..."
    
    # Check if DAG is complete
    if [[ "$DAG_STATE" == "success" ]]; then
        echo -e "\n${GREEN}✅✅✅ PIPELINE COMPLETED SUCCESSFULLY ✅✅✅${NC}"
        break
    elif [[ "$DAG_STATE" == "failed" ]]; then
        echo -e "\n${RED}❌ PIPELINE FAILED${NC}"
        echo -e "${YELLOW}Checking failed tasks...${NC}"
        docker exec $AIRFLOW_CONTAINER airflow tasks states-for-dag-run master_pipeline "$EXECUTION_DATE" | grep "failed"
        break
    fi
    
    # Wait before next check
    sleep 30
done

# Final summary
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}📊 EXECUTION SUMMARY${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Final Task States:${NC}"
get_task_states

echo -e "\n${YELLOW}DAG Run Details:${NC}"
docker exec $AIRFLOW_CONTAINER airflow dags show master_pipeline 2>/dev/null || echo "Unable to fetch DAG details"

echo -e "\n${YELLOW}Useful Commands:${NC}"
echo -e "  View logs: docker exec $AIRFLOW_CONTAINER airflow tasks log master_pipeline <task_id> $EXECUTION_DATE"
echo -e "  Rerun failed: docker exec $AIRFLOW_CONTAINER airflow dags backfill -s $EXECUTION_DATE -e $EXECUTION_DATE --reset-dagruns master_pipeline"
echo -e "  Web UI: http://localhost:8080/dags/master_pipeline/grid"

echo -e "\n${BLUE}===============================================================================${NC}"
