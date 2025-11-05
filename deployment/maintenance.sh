#!/bin/bash

# =============================================================================
# Maintenance Script
# =============================================================================
# This script performs routine maintenance tasks
# Run as: bash maintenance.sh
# Or schedule weekly: 0 2 * * 0 /home/ubuntu/finance_portfolio/deployment/maintenance.sh
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_DIR="/home/ubuntu/finance_portfolio"
BACKUP_DIR="/home/ubuntu/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_DIR/logs/maintenance.log"

# =============================================================================
# Helper Functions
# =============================================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# =============================================================================
# 1. Database Maintenance
# =============================================================================

database_maintenance() {
    print_header "Database Maintenance"
    
    cd "$PROJECT_DIR"
    
    log "Starting database maintenance"
    
    # Vacuum database
    log "Running VACUUM..."
    docker-compose exec -T postgres psql -U airflow airflow -c "VACUUM ANALYZE;" || true
    
    # Update statistics
    log "Updating statistics..."
    docker-compose exec -T postgres psql -U airflow airflow -c "ANALYZE;" || true
    
    # Reindex
    log "Reindexing database..."
    docker-compose exec -T postgres psql -U airflow airflow -c "REINDEX DATABASE airflow;" || true
    
    log "Database maintenance completed"
}

# =============================================================================
# 2. Log Rotation
# =============================================================================

log_rotation() {
    print_header "Log Rotation"
    
    log "Starting log rotation"
    
    # Backend logs
    if [ -d "$PROJECT_DIR/web_executor/backend/logs" ]; then
        find "$PROJECT_DIR/web_executor/backend/logs" -name "*.log" -mtime +7 -exec gzip {} \;
        find "$PROJECT_DIR/web_executor/backend/logs" -name "*.log.gz" -mtime +30 -delete
        log "Backend logs rotated"
    fi
    
    # Airflow logs
    if [ -d "$PROJECT_DIR/airflow/logs" ]; then
        find "$PROJECT_DIR/airflow/logs" -name "*.log" -mtime +7 -exec gzip {} \;
        find "$PROJECT_DIR/airflow/logs" -name "*.log.gz" -mtime +30 -delete
        log "Airflow logs rotated"
    fi
    
    log "Log rotation completed"
}

# =============================================================================
# 3. Docker Cleanup
# =============================================================================

docker_cleanup() {
    print_header "Docker Cleanup"
    
    log "Starting Docker cleanup"
    
    # Remove stopped containers
    STOPPED=$(docker ps -aq -f status=exited | wc -l)
    if [ "$STOPPED" -gt 0 ]; then
        docker rm $(docker ps -aq -f status=exited) 2>/dev/null || true
        log "Removed $STOPPED stopped containers"
    fi
    
    # Remove dangling images
    DANGLING=$(docker images -qf dangling=true | wc -l)
    if [ "$DANGLING" -gt 0 ]; then
        docker rmi $(docker images -qf dangling=true) 2>/dev/null || true
        log "Removed $DANGLING dangling images"
    fi
    
    # Remove unused volumes
    docker volume prune -f
    log "Pruned unused volumes"
    
    # Remove unused networks
    docker network prune -f
    log "Pruned unused networks"
    
    # System prune
    docker system prune -f
    
    log "Docker cleanup completed"
}

# =============================================================================
# 4. Backup Cleanup
# =============================================================================

backup_cleanup() {
    print_header "Backup Cleanup"
    
    log "Starting backup cleanup"
    
    if [ -d "$BACKUP_DIR" ]; then
        # Keep last 7 days
        find "$BACKUP_DIR" -type f -mtime +7 -delete
        
        # Count remaining backups
        BACKUPS=$(find "$BACKUP_DIR" -type f | wc -l)
        log "Cleanup completed, $BACKUPS backups remaining"
    else
        log "Backup directory not found"
    fi
}

# =============================================================================
# 5. SSL Certificate Check
# =============================================================================

ssl_check() {
    print_header "SSL Certificate Check"
    
    log "Checking SSL certificates"
    
    # Check if certbot is installed
    if command -v certbot &> /dev/null; then
        certbot certificates 2>&1 | tee -a "$LOG_FILE"
        
        # Auto-renew if needed
        certbot renew --dry-run 2>&1 | tee -a "$LOG_FILE"
        
        log "SSL check completed"
    else
        log "Certbot not installed, skipping SSL check"
    fi
}

# =============================================================================
# 6. System Updates Check
# =============================================================================

system_updates() {
    print_header "System Updates Check"
    
    log "Checking for system updates"
    
    # Update package list
    sudo apt-get update -qq
    
    # Check for upgradable packages
    UPGRADABLE=$(apt list --upgradable 2>/dev/null | grep -v "Listing" | wc -l)
    
    if [ "$UPGRADABLE" -gt 0 ]; then
        log "⚠️  $UPGRADABLE packages can be upgraded"
        apt list --upgradable 2>/dev/null | tee -a "$LOG_FILE"
    else
        log "✅ System is up to date"
    fi
}

# =============================================================================
# 7. Disk Space Check
# =============================================================================

disk_space_check() {
    print_header "Disk Space Check"
    
    log "Checking disk space"
    
    # Root partition
    DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    log "Root partition usage: ${DISK_USAGE}%"
    
    if [ "$DISK_USAGE" -gt 85 ]; then
        log "⚠️  WARNING: High disk usage!"
        
        # Show largest directories
        log "Largest directories:"
        du -h --max-depth=1 /home/ubuntu | sort -hr | head -10 | tee -a "$LOG_FILE"
    else
        log "✅ Disk space OK"
    fi
    
    # Docker disk usage
    log "Docker disk usage:"
    docker system df | tee -a "$LOG_FILE"
}

# =============================================================================
# 8. Performance Report
# =============================================================================

performance_report() {
    print_header "Performance Report"
    
    log "Generating performance report"
    
    # Uptime
    UPTIME=$(uptime -p)
    log "System uptime: $UPTIME"
    
    # Load average
    LOAD=$(uptime | awk -F'load average:' '{print $2}')
    log "Load average:$LOAD"
    
    # Memory usage
    free -h | tee -a "$LOG_FILE"
    
    # Top processes
    log "Top 5 CPU-consuming processes:"
    ps aux --sort=-%cpu | head -6 | tee -a "$LOG_FILE"
    
    log "Top 5 memory-consuming processes:"
    ps aux --sort=-%mem | head -6 | tee -a "$LOG_FILE"
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    print_header "🔧 Starting Maintenance - $TIMESTAMP"
    
    mkdir -p "$(dirname "$LOG_FILE")"
    
    database_maintenance
    log_rotation
    docker_cleanup
    backup_cleanup
    ssl_check
    system_updates
    disk_space_check
    performance_report
    
    print_header "✅ Maintenance Completed"
    
    log "Maintenance finished successfully"
    echo "Log file: $LOG_FILE"
}

# Run main
main
