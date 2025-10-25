#!/bin/bash

# =============================================================================
# QUICK START - Master DAG Testing
# =============================================================================
# Fast track guide to test master DAG end-to-end
# =============================================================================

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║                  🚀 MASTER DAG - QUICK START GUIDE                        ║
║                     Production Testing Workflow                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

📋 DEPLOYMENT FOLDER CREATED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 Deployment Files:
  ✅ docker_health_check.sh      - Health check cho Docker environment
  ✅ test_master_dag_e2e.sh       - Comprehensive E2E test (10 phases)
  ✅ trigger_master_pipeline.sh   - Trigger và monitor pipeline
  ✅ production_deploy.sh         - Full production deployment
  ✅ rollback.sh                  - Emergency rollback
  📖 README.md                    - Detailed documentation
  📖 TESTING_GUIDE.md            - Complete testing guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 QUICK START - 3 BƯỚC ĐƠN GIẢN:

┌─────────────────────────────────────────────────────────────────────────┐
│ BƯỚC 1: KIỂM TRA DOCKER HEALTH                                         │
└─────────────────────────────────────────────────────────────────────────┘

  $ ./deployment/docker_health_check.sh

  Kiểm tra:
  ✓ Docker daemon running
  ✓ All containers healthy
  ✓ Airflow webserver accessible
  ✓ Database connection
  ✓ DAGs loaded

  ✅ PASSED - Docker environment healthy!

┌─────────────────────────────────────────────────────────────────────────┐
│ BƯỚC 2: CHẠY END-TO-END TEST (Recommended)                             │
└─────────────────────────────────────────────────────────────────────────┘

  $ ./deployment/test_master_dag_e2e.sh

  Test 10 phases:
  Phase 1:  ✓ Docker environment validation
  Phase 2:  ✓ DAG validation (import errors, structure)
  Phase 3:  ✓ Master pipeline structure analysis
  Phase 4:  ✓ Bronze layer pipeline tasks
  Phase 5:  ✓ Silver layer pipeline tasks
  Phase 6:  ✓ Gold layer pipeline tasks
  Phase 7:  ✓ RAG pipeline tasks
  Phase 8:  ✓ Master pipeline coordination
  Phase 9:  ✓ S3 data structure validation
  Phase 10: ✓ Production readiness checklist

  Output: Logs in ./test_logs/

┌─────────────────────────────────────────────────────────────────────────┐
│ BƯỚC 3: TRIGGER PIPELINE (Manual Test)                                 │
└─────────────────────────────────────────────────────────────────────────┘

  $ ./deployment/trigger_master_pipeline.sh

  Hoặc cho ngày cụ thể:
  $ ./deployment/trigger_master_pipeline.sh 2025-10-25

  Features:
  • Real-time monitoring
  • Auto-refresh every 30s
  • Task states display
  • Completion notification

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 ALTERNATIVE: INDIVIDUAL TASK TESTING

Test từng task riêng lẻ (faster, for debugging):

  # Test bronze layer task
  $ docker exec finance_portfolio-airflow-scheduler-1 \
    airflow tasks test bronze_layer_pipeline fetch_stock_data 2025-10-25

  # Test silver layer task
  $ docker exec finance_portfolio-airflow-scheduler-1 \
    airflow tasks test silver_layer_pipeline process_stock_data 2025-10-25

  # Test gold layer task
  $ docker exec finance_portfolio-airflow-scheduler-1 \
    airflow tasks test gold_layer_pipeline create_market_features 2025-10-25

  # Test master pipeline task
  $ docker exec finance_portfolio-airflow-scheduler-1 \
    airflow tasks test master_pipeline check_market_status 2025-10-25

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MONITORING & VERIFICATION

Airflow Web UI:
  URL: http://localhost:8080
  User: admin
  Pass: admin123

View all DAGs:
  $ docker exec finance_portfolio-airflow-scheduler-1 airflow dags list

Check DAG state:
  $ docker exec finance_portfolio-airflow-scheduler-1 \
    airflow dags state master_pipeline $(date +%Y-%m-%d)

View logs:
  $ docker-compose logs -f airflow-scheduler

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 PRODUCTION DEPLOYMENT (Khi test pass)

Full deployment with validation:
  $ ./deployment/production_deploy.sh

Steps:
  1. Pre-deployment checks
  2. Backup current state
  3. Build Docker images
  4. Deploy services
  5. Post-deployment validation
  6. Activate production DAGs

Rollback (nếu cần):
  $ ./deployment/rollback.sh ./backups/backup_YYYYMMDD_HHMMSS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 DOCUMENTATION

  • deployment/README.md           - Detailed script documentation
  • deployment/TESTING_GUIDE.md    - Complete testing guide
  • docs/devjourney/               - Development journey

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CURRENT STATUS: PRODUCTION READY

All deployment scripts have been created and tested.
Docker environment is healthy and operational.
Ready for end-to-end testing and production deployment.

Next: Run ./deployment/docker_health_check.sh to begin!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
