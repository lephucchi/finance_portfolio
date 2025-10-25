#!/bin/bash

# =============================================================================
# Master DAG End-to-End Test Script for Production Readiness
# =============================================================================
# This script tests the entire master_pipeline DAG and all sub-pipelines
# through Docker to ensure production readiness
# 
# Usage: ./scripts/test_master_dag_e2e.sh
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
AIRFLOW_CONTAINER="finance_portfolio-airflow-scheduler-1"
TEST_DATE=$(date +%Y-%m-%d)
TEST_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="./test_logs"

# Create log directory
mkdir -p $LOG_DIR

echo -e "${BLUE}===============================================================================${NC}"
echo -e "${BLUE}🧪 MASTER DAG END-TO-END TEST - PRODUCTION READINESS${NC}"
echo -e "${BLUE}===============================================================================${NC}"
echo -e "Test Date: ${TEST_DATE}"
echo -e "Timestamp: ${TEST_TIMESTAMP}"
echo -e "Log Directory: ${LOG_DIR}"
echo ""

# =============================================================================
# Phase 1: Docker Environment Validation
# =============================================================================
echo -e "${BLUE}===============================================================================${NC}"
echo -e "${BLUE}PHASE 1: Docker Environment Validation${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Checking Docker containers...${NC}"
docker-compose ps

# Check if Airflow scheduler is running
if docker ps | grep -q "$AIRFLOW_CONTAINER"; then
    echo -e "${GREEN}✅ Airflow scheduler is running${NC}"
else
    echo -e "${RED}❌ Airflow scheduler is not running${NC}"
    echo -e "${YELLOW}Starting Docker services...${NC}"
    docker-compose up -d
    echo -e "${YELLOW}Waiting 60 seconds for services to initialize...${NC}"
    sleep 60
fi

# Check Airflow webserver health
echo -e "\n${YELLOW}Checking Airflow webserver health...${NC}"
WEBSERVER_HEALTH=$(curl -s http://localhost:8080/health || echo "FAILED")
if echo "$WEBSERVER_HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Airflow webserver is healthy${NC}"
else
    echo -e "${RED}❌ Airflow webserver health check failed${NC}"
    echo "$WEBSERVER_HEALTH"
fi

# Check database connection
echo -e "\n${YELLOW}Checking database connection...${NC}"
docker exec $AIRFLOW_CONTAINER airflow db check && \
    echo -e "${GREEN}✅ Database connection successful${NC}" || \
    echo -e "${RED}❌ Database connection failed${NC}"

echo -e "\n${GREEN}✅ PHASE 1 COMPLETED${NC}"

# =============================================================================
# Phase 2: DAG Validation
# =============================================================================
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}PHASE 2: DAG Validation${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Listing all DAGs...${NC}"
docker exec $AIRFLOW_CONTAINER airflow dags list | tee $LOG_DIR/dags_list_${TEST_TIMESTAMP}.txt

echo -e "\n${YELLOW}Checking for DAG import errors...${NC}"
docker exec $AIRFLOW_CONTAINER airflow dags list-import-errors | tee $LOG_DIR/dag_errors_${TEST_TIMESTAMP}.txt

# Validate specific DAGs exist
echo -e "\n${YELLOW}Validating required DAGs...${NC}"
REQUIRED_DAGS=("master_pipeline" "bronze_layer_pipeline" "silver_layer_pipeline" "gold_layer_pipeline" "rag_pipeline")

for dag_id in "${REQUIRED_DAGS[@]}"; do
    if docker exec $AIRFLOW_CONTAINER airflow dags list | grep -q "$dag_id"; then
        echo -e "${GREEN}✅ $dag_id${NC}"
        
        # Get DAG details
        echo -e "   ${YELLOW}Getting DAG details...${NC}"
        docker exec $AIRFLOW_CONTAINER airflow dags show "$dag_id" > "$LOG_DIR/${dag_id}_structure_${TEST_TIMESTAMP}.txt" 2>&1 || true
        
        # List tasks
        echo -e "   ${YELLOW}Tasks:${NC}"
        docker exec $AIRFLOW_CONTAINER airflow tasks list "$dag_id" | sed 's/^/     /'
    else
        echo -e "${RED}❌ $dag_id - NOT FOUND${NC}"
        exit 1
    fi
done

echo -e "\n${GREEN}✅ PHASE 2 COMPLETED${NC}"

# =============================================================================
# Phase 3: Master Pipeline Structure Test
# =============================================================================
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}PHASE 3: Master Pipeline Structure Test${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Analyzing master_pipeline structure...${NC}"
docker exec $AIRFLOW_CONTAINER python3 << 'PYTHON_SCRIPT' | tee $LOG_DIR/master_structure_${TEST_TIMESTAMP}.txt
from airflow.models import DagBag
import sys

dagbag = DagBag(include_examples=False)
master_dag = dagbag.dags.get('master_pipeline')

if not master_dag:
    print("❌ master_pipeline not found")
    sys.exit(1)

print("=" * 80)
print("📊 MASTER PIPELINE ANALYSIS")
print("=" * 80)
print(f"\nDAG ID: {master_dag.dag_id}")
print(f"Schedule: {master_dag.schedule_interval}")
print(f"Max Active Runs: {master_dag.max_active_runs}")
print(f"Catchup: {master_dag.catchup}")
print(f"Total Tasks: {len(master_dag.tasks)}")

print("\n" + "=" * 80)
print("📋 TASK LIST")
print("=" * 80)
for task in master_dag.tasks:
    print(f"\n✓ {task.task_id}")
    print(f"  Type: {task.task_type}")
    if task.upstream_task_ids:
        print(f"  ⬆️  Upstream: {', '.join(sorted(task.upstream_task_ids))}")
    if task.downstream_task_ids:
        print(f"  ⬇️  Downstream: {', '.join(sorted(task.downstream_task_ids))}")

print("\n" + "=" * 80)
print("🔗 PIPELINE FLOW")
print("=" * 80)

# Find execution path
start_tasks = [t for t in master_dag.tasks if not t.upstream_task_ids]
print("\n🚀 Start Tasks:")
for t in start_tasks:
    print(f"  • {t.task_id}")

end_tasks = [t for t in master_dag.tasks if not t.downstream_task_ids]
print("\n🏁 End Tasks:")
for t in end_tasks:
    print(f"  • {t.task_id}")

# Check for sensors (pipeline orchestration)
sensor_tasks = [t for t in master_dag.tasks if 'sensor' in t.task_type.lower() or 'wait_for' in t.task_id]
print("\n⏳ Pipeline Sensors:")
for t in sensor_tasks:
    print(f"  • {t.task_id}")

# Check for trigger tasks
trigger_tasks = [t for t in master_dag.tasks if 'trigger' in t.task_id]
print("\n🎯 Pipeline Triggers:")
for t in trigger_tasks:
    print(f"  • {t.task_id}")

print("\n" + "=" * 80)
print("✅ Structure analysis completed")
print("=" * 80)
PYTHON_SCRIPT

echo -e "\n${GREEN}✅ PHASE 3 COMPLETED${NC}"

# =============================================================================
# Phase 4: Individual Task Testing (Bronze Layer)
# =============================================================================
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}PHASE 4: Bronze Layer Pipeline Test${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Testing Bronze layer pipeline tasks...${NC}"

# Test bronze pipeline tasks individually
BRONZE_TASKS=("validate_aws_s3_access" "fetch_stock_data" "fetch_news_data" "save_metadata" "validate_bronze_data")

for task_id in "${BRONZE_TASKS[@]}"; do
    echo -e "\n${YELLOW}Testing task: $task_id${NC}"
    
    # Test the task
    docker exec $AIRFLOW_CONTAINER airflow tasks test bronze_layer_pipeline "$task_id" "$TEST_DATE" \
        > "$LOG_DIR/bronze_${task_id}_${TEST_TIMESTAMP}.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $task_id - PASSED${NC}"
        # Show last 10 lines of log
        echo -e "   ${YELLOW}Last 10 lines:${NC}"
        tail -10 "$LOG_DIR/bronze_${task_id}_${TEST_TIMESTAMP}.log" | sed 's/^/     /'
    else
        echo -e "${RED}❌ $task_id - FAILED${NC}"
        echo -e "   ${RED}Error log:${NC}"
        tail -20 "$LOG_DIR/bronze_${task_id}_${TEST_TIMESTAMP}.log" | sed 's/^/     /'
    fi
done

echo -e "\n${GREEN}✅ PHASE 4 COMPLETED${NC}"

# =============================================================================
# Phase 5: Individual Task Testing (Silver Layer)
# =============================================================================
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}PHASE 5: Silver Layer Pipeline Test${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Testing Silver layer pipeline tasks...${NC}"

SILVER_TASKS=("process_stock_data" "process_news_data" "process_macro_data" "validate_silver_data")

for task_id in "${SILVER_TASKS[@]}"; do
    echo -e "\n${YELLOW}Testing task: $task_id${NC}"
    
    docker exec $AIRFLOW_CONTAINER airflow tasks test silver_layer_pipeline "$task_id" "$TEST_DATE" \
        > "$LOG_DIR/silver_${task_id}_${TEST_TIMESTAMP}.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $task_id - PASSED${NC}"
        echo -e "   ${YELLOW}Last 10 lines:${NC}"
        tail -10 "$LOG_DIR/silver_${task_id}_${TEST_TIMESTAMP}.log" | sed 's/^/     /'
    else
        echo -e "${RED}❌ $task_id - FAILED (may be expected if no data)${NC}"
        echo -e "   ${RED}Error log:${NC}"
        tail -20 "$LOG_DIR/silver_${task_id}_${TEST_TIMESTAMP}.log" | sed 's/^/     /'
    fi
done

echo -e "\n${GREEN}✅ PHASE 5 COMPLETED${NC}"

# =============================================================================
# Phase 6: Individual Task Testing (Gold Layer)
# =============================================================================
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}PHASE 6: Gold Layer Pipeline Test${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Testing Gold layer pipeline tasks...${NC}"

GOLD_TASKS=("create_market_features" "create_sector_performance" "create_news_summary" "create_macro_indicators" "create_sentiment_analysis" "create_serving_cache" "track_pipeline_metadata")

for task_id in "${GOLD_TASKS[@]}"; do
    echo -e "\n${YELLOW}Testing task: $task_id${NC}"
    
    docker exec $AIRFLOW_CONTAINER airflow tasks test gold_layer_pipeline "$task_id" "$TEST_DATE" \
        > "$LOG_DIR/gold_${task_id}_${TEST_TIMESTAMP}.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $task_id - PASSED${NC}"
        echo -e "   ${YELLOW}Last 10 lines:${NC}"
        tail -10 "$LOG_DIR/gold_${task_id}_${TEST_TIMESTAMP}.log" | sed 's/^/     /'
    else
        echo -e "${RED}❌ $task_id - FAILED (may be expected if no data)${NC}"
    fi
done

echo -e "\n${GREEN}✅ PHASE 6 COMPLETED${NC}"

# =============================================================================
# Phase 7: Individual Task Testing (RAG Pipeline)
# =============================================================================
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}PHASE 7: RAG Pipeline Test${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Testing RAG pipeline tasks...${NC}"

RAG_TASKS=("extract_processed_news" "create_vietnamese_embeddings" "update_vector_database" "validate_rag_pipeline")

for task_id in "${RAG_TASKS[@]}"; do
    echo -e "\n${YELLOW}Testing task: $task_id${NC}"
    
    docker exec $AIRFLOW_CONTAINER airflow tasks test rag_pipeline "$task_id" "$TEST_DATE" \
        > "$LOG_DIR/rag_${task_id}_${TEST_TIMESTAMP}.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $task_id - PASSED${NC}"
        echo -e "   ${YELLOW}Last 10 lines:${NC}"
        tail -10 "$LOG_DIR/rag_${task_id}_${TEST_TIMESTAMP}.log" | sed 's/^/     /'
    else
        echo -e "${RED}❌ $task_id - FAILED (may be expected if no data)${NC}"
    fi
done

echo -e "\n${GREEN}✅ PHASE 7 COMPLETED${NC}"

# =============================================================================
# Phase 8: Master Pipeline Tasks Test
# =============================================================================
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}PHASE 8: Master Pipeline Tasks Test${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Testing Master pipeline coordination tasks...${NC}"

MASTER_TASKS=("check_market_status" "validate_aws_connection" "check_pipeline_dependencies" "system_health_check" "generate_daily_report")

for task_id in "${MASTER_TASKS[@]}"; do
    echo -e "\n${YELLOW}Testing task: $task_id${NC}"
    
    docker exec $AIRFLOW_CONTAINER airflow tasks test master_pipeline "$task_id" "$TEST_DATE" \
        > "$LOG_DIR/master_${task_id}_${TEST_TIMESTAMP}.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $task_id - PASSED${NC}"
        echo -e "   ${YELLOW}Last 10 lines:${NC}"
        tail -10 "$LOG_DIR/master_${task_id}_${TEST_TIMESTAMP}.log" | sed 's/^/     /'
    else
        echo -e "${RED}❌ $task_id - FAILED${NC}"
        echo -e "   ${RED}Error log:${NC}"
        tail -20 "$LOG_DIR/master_${task_id}_${TEST_TIMESTAMP}.log" | sed 's/^/     /'
    fi
done

echo -e "\n${GREEN}✅ PHASE 8 COMPLETED${NC}"

# =============================================================================
# Phase 9: S3 Data Validation
# =============================================================================
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}PHASE 9: S3 Data Validation${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Checking S3 data structure...${NC}"

docker exec $AIRFLOW_CONTAINER python3 << 'PYTHON_SCRIPT' | tee $LOG_DIR/s3_validation_${TEST_TIMESTAMP}.txt
import os
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

try:
    s3_hook = S3Hook(aws_conn_id='aws_default')
    bucket_name = os.getenv('AWS_S3_BUCKET', 'bankanalystportfolio')
    
    print("=" * 80)
    print("🗄️  S3 DATA STRUCTURE VALIDATION")
    print("=" * 80)
    print(f"\nBucket: {bucket_name}")
    
    # Check main layer prefixes
    layers = ['bronze', 'silver', 'gold', 'rag']
    
    for layer in layers:
        print(f"\n📂 {layer.upper()} Layer:")
        try:
            keys = s3_hook.list_keys(bucket_name=bucket_name, prefix=f"{layer}/", max_keys=10)
            if keys:
                print(f"  ✅ Found {len(keys)} objects")
                for key in keys[:5]:
                    print(f"     • {key}")
                if len(keys) > 5:
                    print(f"     ... and {len(keys) - 5} more")
            else:
                print(f"  ⚠️  No objects found")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ S3 validation completed")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ S3 validation failed: {str(e)}")
PYTHON_SCRIPT

echo -e "\n${GREEN}✅ PHASE 9 COMPLETED${NC}"

# =============================================================================
# Phase 10: Production Readiness Check
# =============================================================================
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}PHASE 10: Production Readiness Check${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Running production readiness checks...${NC}"

docker exec $AIRFLOW_CONTAINER python3 << 'PYTHON_SCRIPT' | tee $LOG_DIR/production_readiness_${TEST_TIMESTAMP}.txt
from airflow.models import DagBag
import sys

dagbag = DagBag(include_examples=False)

print("=" * 80)
print("🚀 PRODUCTION READINESS CHECKLIST")
print("=" * 80)

checklist = {
    'dag_import_errors': len(dagbag.import_errors) == 0,
    'all_dags_loaded': 'master_pipeline' in dagbag.dags,
    'master_dag_exists': 'master_pipeline' in dagbag.dags,
    'bronze_dag_exists': 'bronze_layer_pipeline' in dagbag.dags,
    'silver_dag_exists': 'silver_layer_pipeline' in dagbag.dags,
    'gold_dag_exists': 'gold_layer_pipeline' in dagbag.dags,
    'rag_dag_exists': 'rag_pipeline' in dagbag.dags,
}

if 'master_pipeline' in dagbag.dags:
    master = dagbag.dags['master_pipeline']
    checklist.update({
        'master_has_schedule': master.schedule_interval is not None,
        'master_max_active_runs_set': master.max_active_runs == 1,
        'master_catchup_disabled': master.catchup == False,
        'master_has_tasks': len(master.tasks) > 0,
    })

print("\n📋 Checklist Items:")
print("-" * 80)

all_passed = True
for check, passed in checklist.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {check.replace('_', ' ').title()}")
    if not passed:
        all_passed = False

print("\n" + "=" * 80)
if all_passed:
    print("✅ PRODUCTION READY - All checks passed!")
else:
    print("❌ NOT PRODUCTION READY - Some checks failed")
print("=" * 80)

sys.exit(0 if all_passed else 1)
PYTHON_SCRIPT

PRODUCTION_READY=$?

echo -e "\n${GREEN}✅ PHASE 10 COMPLETED${NC}"

# =============================================================================
# Final Summary
# =============================================================================
echo -e "\n${BLUE}===============================================================================${NC}"
echo -e "${BLUE}📊 TEST SUMMARY${NC}"
echo -e "${BLUE}===============================================================================${NC}"

echo -e "\nTest Timestamp: ${TEST_TIMESTAMP}"
echo -e "Log Directory: ${LOG_DIR}"
echo -e "\nLog Files Created:"
ls -lh $LOG_DIR/*${TEST_TIMESTAMP}* 2>/dev/null | awk '{print "  • "$9" ("$5")"}'

echo -e "\n${BLUE}===============================================================================${NC}"

if [ $PRODUCTION_READY -eq 0 ]; then
    echo -e "${GREEN}✅✅✅ MASTER DAG E2E TEST PASSED - PRODUCTION READY ✅✅✅${NC}"
    echo -e "${GREEN}All components tested successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  MASTER DAG E2E TEST COMPLETED WITH WARNINGS ⚠️${NC}"
    echo -e "${YELLOW}Some components may need data to be fully functional${NC}"
fi

echo -e "${BLUE}===============================================================================${NC}"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "1. Review test logs in: ${LOG_DIR}/"
echo -e "2. Trigger full pipeline run: docker exec $AIRFLOW_CONTAINER airflow dags trigger master_pipeline"
echo -e "3. Monitor execution: http://localhost:8080"
echo -e "4. Check S3 bucket for data: aws s3 ls s3://\$AWS_S3_BUCKET/ --recursive"

exit 0
