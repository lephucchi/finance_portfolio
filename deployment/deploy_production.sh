#!/bin/bash

# =============================================================================
# Production Deployment Script
# =============================================================================
# This script deploys the Finance Portfolio application to production
# Run as: bash deploy_production.sh
# =============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_DIR="/home/ubuntu/finance_portfolio"
BACKUP_DIR="/home/ubuntu/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Service URLs - Use environment variables or container names in docker-compose
# In production with docker-compose, use service names
# For standalone, use localhost:port
BACKEND_HEALTH_URL="${BACKEND_HEALTH_URL:-http://localhost:8000/health}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5173}"

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# =============================================================================
# Pre-deployment Checks
# =============================================================================

check_prerequisites() {
    print_header "Running Pre-deployment Checks"
    
    # Check if docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running"
        exit 1
    fi
    print_success "Docker is running"
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed"
        exit 1
    fi
    print_success "docker-compose is available"
    
    # Check if .env files exist
    if [ ! -f "${PROJECT_DIR}/airflow/.env" ]; then
        print_error "airflow/.env not found"
        exit 1
    fi
    if [ ! -f "${PROJECT_DIR}/web_executor/backend/.env" ]; then
        print_error "backend/.env not found"
        exit 1
    fi
    if [ ! -f "${PROJECT_DIR}/web_executor/frontend/.env" ]; then
        print_error "frontend/.env not found"
        exit 1
    fi
    print_success "Environment files found"
}

# =============================================================================
# Backup Current Deployment
# =============================================================================

create_backup() {
    print_header "Creating Backup"
    
    mkdir -p ${BACKUP_DIR}
    
    # Backup docker volumes
    cd ${PROJECT_DIR}
    docker-compose exec -T postgres pg_dump -U airflow airflow > ${BACKUP_DIR}/postgres_${TIMESTAMP}.sql || true
    
    # Backup logs
    tar -czf ${BACKUP_DIR}/logs_${TIMESTAMP}.tar.gz ${PROJECT_DIR}/web_executor/backend/logs || true
    tar -czf ${BACKUP_DIR}/airflow_logs_${TIMESTAMP}.tar.gz ${PROJECT_DIR}/airflow/logs || true
    
    print_success "Backup created at ${BACKUP_DIR}"
}

# =============================================================================
# Pull Latest Code
# =============================================================================

pull_latest_code() {
    print_header "Pulling Latest Code"
    
    cd ${PROJECT_DIR}
    
    # Stash any local changes
    git stash
    
    # Pull latest
    git pull origin main
    
    print_success "Code updated to latest version"
    git log -1 --oneline
}

# =============================================================================
# Build Docker Images
# =============================================================================

build_images() {
    print_header "Building Docker Images"
    
    cd ${PROJECT_DIR}
    
    # Build all images
    docker-compose build --no-cache
    
    print_success "Docker images built successfully"
}

# =============================================================================
# Stop Current Services
# =============================================================================

stop_services() {
    print_header "Stopping Current Services"
    
    cd ${PROJECT_DIR}
    docker-compose down
    
    print_success "Services stopped"
}

# =============================================================================
# Start Services
# =============================================================================

start_services() {
    print_header "Starting Services"
    
    cd ${PROJECT_DIR}
    docker-compose up -d
    
    print_success "Services started"
}

# =============================================================================
# Health Checks
# =============================================================================

wait_for_services() {
    print_header "Waiting for Services to be Healthy"
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f "$BACKEND_HEALTH_URL" > /dev/null 2>&1; then
            print_success "Backend is healthy"
            break
        fi
        attempt=$((attempt + 1))
        echo "Waiting for backend... ($attempt/$max_attempts)"
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Backend failed to become healthy"
        return 1
    fi
    
    # Check frontend
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -f "$FRONTEND_URL" > /dev/null 2>&1; then
            print_success "Frontend is healthy"
            break
        fi
        attempt=$((attempt + 1))
        echo "Waiting for frontend... ($attempt/$max_attempts)"
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Frontend failed to become healthy"
        return 1
    fi
    
    print_success "All services are healthy"
}

# =============================================================================
# Post-deployment Tasks
# =============================================================================

post_deployment() {
    print_header "Running Post-deployment Tasks"
    
    # Clean up old images
    docker image prune -f
    
    # Clean up old backups (keep last 7)
    find ${BACKUP_DIR} -type f -mtime +7 -delete
    
    print_success "Cleanup completed"
}

# =============================================================================
# Display Status
# =============================================================================

display_status() {
    print_header "Deployment Summary"
    
    echo -e "${GREEN}Services Status:${NC}"
    docker-compose ps
    
    echo -e "\n${GREEN}Service URLs:${NC}"
    echo "  Backend Health:  $BACKEND_HEALTH_URL"
    echo "  Frontend:        $FRONTEND_URL"
    
    # Get public IP if available
    PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")
    
    echo -e "\n${GREEN}Access URLs (replace YOUR_SERVER_IP with your EC2 public IP):${NC}"
    echo "  Frontend:    http://$PUBLIC_IP:5173"
    echo "  Backend API: http://$PUBLIC_IP:8000"
    echo "  API Docs:    http://$PUBLIC_IP:8000/docs"
    echo "  Airflow:     http://$PUBLIC_IP:8080"
    
    echo -e "\n${GREEN}Useful Commands:${NC}"
    echo "  View logs:       docker-compose logs -f"
    echo "  Restart:         docker-compose restart"
    echo "  Stop:            docker-compose stop"
    echo "  View status:     docker-compose ps"
    echo "  Rollback:        bash deployment/rollback.sh ${TIMESTAMP}"
}

# =============================================================================
# Rollback Function
# =============================================================================

rollback() {
    print_header "Rolling Back Deployment"
    
    local backup_timestamp=$1
    
    if [ -z "$backup_timestamp" ]; then
        print_error "Backup timestamp required"
        echo "Usage: bash deploy_production.sh rollback <timestamp>"
        exit 1
    fi
    
    cd ${PROJECT_DIR}
    
    # Stop services
    docker-compose down
    
    # Restore database
    if [ -f "${BACKUP_DIR}/postgres_${backup_timestamp}.sql" ]; then
        docker-compose up -d postgres
        sleep 10
        cat ${BACKUP_DIR}/postgres_${backup_timestamp}.sql | docker-compose exec -T postgres psql -U airflow airflow
        print_success "Database restored"
    fi
    
    # Restore logs
    if [ -f "${BACKUP_DIR}/logs_${backup_timestamp}.tar.gz" ]; then
        tar -xzf ${BACKUP_DIR}/logs_${backup_timestamp}.tar.gz -C /
        print_success "Logs restored"
    fi
    
    # Restart services
    docker-compose up -d
    
    print_success "Rollback completed"
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    print_header "🚀 Starting Production Deployment"
    
    # Check for rollback
    if [ "$1" == "rollback" ]; then
        rollback $2
        exit 0
    fi
    
    # Run deployment
    check_prerequisites
    create_backup
    pull_latest_code
    stop_services
    build_images
    start_services
    wait_for_services
    post_deployment
    display_status
    
    print_header "🎉 Deployment Complete!"
}

# Run main
main "$@"
