# 🚀 Deployment Guide

Complete guide for deploying Finance Portfolio to production on AWS EC2.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [EC2 Setup](#ec2-setup)
- [Initial Deployment](#initial-deployment)
- [CI/CD Setup](#cicd-setup)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## ✅ Prerequisites

### AWS Resources

- **EC2 Instance**: t2.large or better (t2.medium minimum)
- **Security Group**: Ports 22, 80, 443, 5173, 8000, 8080
- **Elastic IP**: Static IP address
- **IAM User**: With S3, Athena, Glue access
- **Domain (Optional)**: For HTTPS with SSL

### Local Tools

```bash
# Required
- AWS CLI v2
- SSH client
- Git
- Docker (for testing)

# Verify installations
aws --version
ssh -V
git --version
docker --version
```

---

## 🖥️ EC2 Setup

### Step 1: Launch EC2 Instance

```bash
# Launch Ubuntu 22.04 LTS instance
# Instance type: t2.large (4GB RAM minimum)
# Storage: 30GB GP3 SSD
# Key pair: Create and download .pem file
```

### Step 2: Configure Security Group

```bash
# Inbound Rules
Port 22   (SSH)         - Your IP only
Port 80   (HTTP)        - 0.0.0.0/0
Port 443  (HTTPS)       - 0.0.0.0/0
Port 5173 (Frontend)    - 0.0.0.0/0 (temporary, use Nginx later)
Port 8000 (Backend)     - 0.0.0.0/0 (temporary, use Nginx later)
Port 8080 (Airflow)     - Your IP only
```

### Step 3: Connect to EC2

```bash
# Set key permissions
chmod 400 your-key.pem

# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update hostname (optional)
sudo hostnamectl set-hostname finance-portfolio
```

### Step 4: Run Setup Script

```bash
# Copy setup script to EC2
scp -i your-key.pem deployment/setup_ec2.sh ubuntu@your-ec2-ip:~

# Run setup script
chmod +x setup_ec2.sh
sudo bash setup_ec2.sh

# This will install:
# - Docker & Docker Compose
# - Nginx
# - Certbot (SSL)
# - AWS CLI
# - Monitoring tools
# - Configure firewall
# - Create swap file
```

### Step 5: Logout and Login

```bash
# Logout to apply docker group
exit

# Login again
ssh -i your-key.pem ubuntu@your-ec2-ip

# Verify docker works without sudo
docker ps
```

---

## 📦 Initial Deployment

### Step 1: Clone Repository

```bash
cd ~
git clone https://github.com/lephucchi/finance_portfolio.git
cd finance_portfolio
```

### Step 2: Configure Environment

```bash
# Airflow
cp airflow/.env.example airflow/.env
nano airflow/.env
# Update:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - _AIRFLOW_WWW_USER_PASSWORD

# Backend
cp web_executor/backend/.env.example web_executor/backend/.env
nano web_executor/backend/.env
# Update:
# - AWS credentials
# - SUPABASE_URL
# - SUPABASE_KEY
# - GEMINI_API_KEY

# Frontend
cp web_executor/frontend/.env.example web_executor/frontend/.env
nano web_executor/frontend/.env
# Update:
# - VITE_API_BASE_URL=http://your-ec2-ip:8000/api/v1
```

### Step 3: Deploy with Docker Compose

```bash
# Using the deployment script
bash deploy.sh
# Select option 1 (Full Stack)

# OR manually
docker-compose build
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 4: Verify Deployment

```bash
# Backend health
curl http://localhost:8000/health

# Frontend
curl http://localhost:5173

# Airflow
curl http://localhost:8080/health

# All services should return 200 OK
```

---

## 🔄 CI/CD Setup

### Step 1: GitHub Secrets

Add these secrets in GitHub repository settings:

```bash
# Settings > Secrets and variables > Actions > New repository secret

AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
EC2_HOST=<your-ec2-public-ip>
EC2_SSH_PRIVATE_KEY=<paste-your-pem-file-content>
```

### Step 2: Create ECR Repositories

```bash
# Login to AWS
aws configure

# Create ECR repositories
aws ecr create-repository --repository-name finance-backend --region ap-southeast-1
aws ecr create-repository --repository-name finance-frontend --region ap-southeast-1

# Note the repository URIs
```

### Step 3: Test CI/CD Pipeline

```bash
# Make a change
git checkout -b test-cicd
echo "# Test" >> README.md
git add .
git commit -m "test: CI/CD pipeline"
git push origin test-cicd

# Create pull request on GitHub
# Pipeline will run tests

# Merge to main
# Pipeline will build, push to ECR, and deploy
```

### Step 4: Verify Automated Deployment

```bash
# Check GitHub Actions
# https://github.com/lephucchi/finance_portfolio/actions

# On EC2, verify new version
ssh ubuntu@your-ec2-ip
cd ~/finance_portfolio
docker-compose ps
docker-compose logs -f backend frontend
```

---

## 🌐 Nginx Configuration (Optional but Recommended)

### Step 1: Configure Nginx

```bash
# Copy nginx config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/finance-portfolio

# Update domain name
sudo nano /etc/nginx/sites-available/finance-portfolio
# Replace 'your-domain.com' with actual domain

# Enable site
sudo ln -s /etc/nginx/sites-available/finance-portfolio /etc/nginx/sites-enabled/

# Remove default
sudo rm /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Step 2: Setup SSL with Let's Encrypt

```bash
# Run certbot
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts
# - Enter email
# - Agree to terms
# - Auto-redirect HTTP to HTTPS: Yes

# Verify SSL
curl https://your-domain.com/health

# Auto-renewal is configured by certbot
# Test renewal
sudo certbot renew --dry-run
```

### Step 3: Update Frontend Environment

```bash
# Update frontend .env
nano web_executor/frontend/.env
# Change to:
# VITE_API_BASE_URL=https://your-domain.com/api/v1

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

---

## 📊 Monitoring

### Application Logs

```bash
# Real-time logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f airflow-scheduler

# Last 100 lines
docker-compose logs --tail=100 backend
```

### System Monitoring

```bash
# Resource usage
docker stats

# Disk usage
df -h
docker system df

# Memory
free -h

# Process monitoring
htop

# Network
sudo nethogs
```

### Health Checks

```bash
# Create monitoring script
cat > ~/monitor.sh << 'EOF'
#!/bin/bash
echo "=== Health Check $(date) ==="
echo "Backend: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)"
echo "Frontend: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173)"
echo "Airflow: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)"
echo ""
docker-compose ps
EOF

chmod +x ~/monitor.sh

# Run monitoring
./monitor.sh
```

### CloudWatch Integration (Optional)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure CloudWatch
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard

# Start agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

---

## 🔧 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Check disk space
df -h

# Check memory
free -h

# Restart specific service
docker-compose restart backend

# Full restart
docker-compose down
docker-compose up -d
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker-compose exec postgres psql -U airflow -c "SELECT 1"

# Reset database
docker-compose down -v
docker-compose up -d
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000
sudo lsof -i :5173

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

### Out of Memory

```bash
# Check memory
free -h

# Increase swap
sudo swapoff /swapfile
sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
sudo mkswap /swapfile
sudo swapon /swapfile

# Restart services
docker-compose restart
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Force renewal
sudo certbot renew --force-renewal

# Check expiration
sudo certbot certificates
```

### Rollback Deployment

```bash
# Use deployment script
cd ~/finance_portfolio
bash deployment/deploy_production.sh rollback <timestamp>

# Or manually
git reset --hard HEAD~1
docker-compose down
docker-compose up -d
```

---

## 🎯 Production Checklist

Before going live:

- [ ] All .env files configured
- [ ] SSL certificate installed
- [ ] Security groups configured
- [ ] Backups automated
- [ ] Monitoring setup
- [ ] Domain DNS configured
- [ ] Firewall rules tested
- [ ] Health checks passing
- [ ] CI/CD pipeline tested
- [ ] Documentation updated

---

## 📞 Support

For issues:

1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check GitHub Issues
4. Contact: lephucchi@github.com

---

**Last Updated**: November 5, 2025
