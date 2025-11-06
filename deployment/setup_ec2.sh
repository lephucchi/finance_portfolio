#!/bin/bash

# =============================================================================
# EC2 Ubuntu Server Setup Script
# =============================================================================
# This script prepares an Ubuntu EC2 instance for deployment
# Run as: sudo bash setup_ec2.sh
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="finance_portfolio"
PROJECT_DIR="/home/ubuntu/${PROJECT_NAME}"
DOCKER_COMPOSE_VERSION="2.23.0"

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

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
    print_success "Running as root"
}

# =============================================================================
# System Update
# =============================================================================

update_system() {
    print_header "Updating System Packages"
    apt-get update -y
    apt-get upgrade -y
    apt-get install -y curl wget git vim htop unzip
    print_success "System updated"
}

# =============================================================================
# Docker Installation
# =============================================================================

install_docker() {
    print_header "Installing Docker"
    
    # Remove old versions
    apt-get remove -y docker docker-engine docker.io containerd runc || true
    
    # Install dependencies
    apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    # Add ubuntu user to docker group
    usermod -aG docker ubuntu
    
    print_success "Docker installed: $(docker --version)"
}

# =============================================================================
# Docker Compose Installation
# =============================================================================

install_docker_compose() {
    print_header "Installing Docker Compose"
    
    # Download docker-compose
    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    
    # Make executable
    chmod +x /usr/local/bin/docker-compose
    
    # Create symlink
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    print_success "Docker Compose installed: $(docker-compose --version)"
}

# =============================================================================
# Nginx Installation
# =============================================================================

install_nginx() {
    print_header "Installing Nginx"
    
    apt-get install -y nginx
    systemctl start nginx
    systemctl enable nginx
    
    print_success "Nginx installed and running"
}

# =============================================================================
# Certbot (SSL) Installation
# =============================================================================

install_certbot() {
    print_header "Installing Certbot for SSL"
    
    apt-get install -y certbot python3-certbot-nginx
    
    print_success "Certbot installed"
    print_warning "Run manually: sudo certbot --nginx -d your-domain.com"
}

# =============================================================================
# AWS CLI Installation
# =============================================================================

install_aws_cli() {
    print_header "Installing AWS CLI"
    
    cd /tmp
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip -q awscliv2.zip
    ./aws/install
    rm -rf aws awscliv2.zip
    
    print_success "AWS CLI installed: $(aws --version)"
}

# =============================================================================
# Firewall Configuration
# =============================================================================

configure_firewall() {
    print_header "Configuring UFW Firewall"
    
    # Install UFW if not present
    apt-get install -y ufw
    
    # Allow SSH (important!)
    ufw allow 22/tcp
    
    # Allow HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Allow application ports
    ufw allow 5173/tcp  # Frontend
    ufw allow 8000/tcp  # Backend
    ufw allow 8080/tcp  # Airflow
    
    # Enable firewall (only if running interactively)
    if [ -t 0 ]; then
        ufw --force enable
        print_success "Firewall configured and enabled"
    else
        print_warning "Firewall configured but not enabled (non-interactive mode)"
    fi
    
    ufw status
}

# =============================================================================
# Create Project Structure
# =============================================================================

setup_project_structure() {
    print_header "Setting Up Project Structure"
    
    # Create project directory
    mkdir -p ${PROJECT_DIR}
    mkdir -p ${PROJECT_DIR}/logs
    mkdir -p ${PROJECT_DIR}/data
    mkdir -p ${PROJECT_DIR}/backups
    
    # Set ownership
    chown -R ubuntu:ubuntu ${PROJECT_DIR}
    
    print_success "Project directories created at ${PROJECT_DIR}"
}

# =============================================================================
# System Monitoring Tools
# =============================================================================

install_monitoring() {
    print_header "Installing Monitoring Tools"
    
    apt-get install -y htop iotop nethogs ncdu
    
    print_success "Monitoring tools installed"
}

# =============================================================================
# Swap File Creation (for t2.micro)
# =============================================================================

create_swap() {
    print_header "Creating Swap File (2GB)"
    
    # Check if swap already exists
    if swapon --show | grep -q '/swapfile'; then
        print_warning "Swap file already exists"
        return
    fi
    
    # Create swap file
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    
    # Make swap permanent
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    
    # Configure swappiness
    echo 'vm.swappiness=10' >> /etc/sysctl.conf
    sysctl -p
    
    print_success "Swap file created (2GB)"
    free -h
}

# =============================================================================
# Environment File Template
# =============================================================================

create_env_template() {
    print_header "Creating Environment Template"
    
    cat > ${PROJECT_DIR}/.env.template << 'EOF'
# =============================================================================
# Finance Portfolio - Environment Configuration
# =============================================================================

# AWS Configuration
AWS_REGION=ap-southeast-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET=bankanalystportfolio

# Airflow Configuration
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=change_this_password

# Backend Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_api_key

# Frontend Configuration
# Update this to your domain/IP in production
VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://localhost:8000/api/v1}

# Database
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
EOF
    
    chown ubuntu:ubuntu ${PROJECT_DIR}/.env.template
    print_success "Environment template created at ${PROJECT_DIR}/.env.template"
}

# =============================================================================
# System Limits Configuration
# =============================================================================

configure_limits() {
    print_header "Configuring System Limits"
    
    cat >> /etc/security/limits.conf << EOF

# Finance Portfolio - Increased limits
ubuntu soft nofile 65536
ubuntu hard nofile 65536
ubuntu soft nproc 32768
ubuntu hard nproc 32768
EOF
    
    print_success "System limits configured"
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    print_header "🚀 Starting EC2 Ubuntu Setup for Finance Portfolio"
    
    check_root
    update_system
    install_docker
    install_docker_compose
    install_nginx
    install_certbot
    install_aws_cli
    install_monitoring
    setup_project_structure
    create_swap
    configure_firewall
    configure_limits
    create_env_template
    
    print_header "🎉 Setup Complete!"
    echo ""
    echo "Next Steps:"
    echo "1. Logout and login again to apply docker group permissions"
    echo "2. Clone your repository: git clone https://github.com/lephucchi/finance_portfolio.git"
    echo "3. Copy and configure .env files"
    echo "4. Run: cd finance_portfolio && docker-compose up -d"
    echo ""
    print_success "All done! 🚀"
}

# Run main function
main
