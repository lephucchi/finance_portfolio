# 🚀 EC2 Deployment Checklist - Finance Portfolio

## ✅ Thông tin EC2 Instance

```
AMI: Amazon Linux 2023 AMI 2023.9.20251105.0 x86_64 HVM kernel-6.1
Instance Type: m7i-flex.large
Storage: 20 GiB
Region: ap-southeast-1 (Singapore)
```

## 📋 Pre-Deployment Checklist

### 1. ⚙️ Cấu hình Security Group

Đảm bảo Security Group có các rules sau:

```
Inbound Rules:
- SSH (22): Your IP / 0.0.0.0/0
- HTTP (80): 0.0.0.0/0
- HTTPS (443): 0.0.0.0/0
- Custom TCP (5173): 0.0.0.0/0  # Frontend
- Custom TCP (8000): 0.0.0.0/0  # Backend API
- Custom TCP (8080): 0.0.0.0/0  # Airflow Web UI
- PostgreSQL (5432): Security Group itself  # For internal Docker network

Outbound Rules:
- All traffic: 0.0.0.0/0
```

### 2. 🔑 SSH Key Pair

```bash
# Đảm bảo đã download .pem file
chmod 400 your-key.pem
ssh -i your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

### 3. 📦 Chuẩn bị Environment Variables

Chuẩn bị các giá trị sau trước khi deploy:

```
✅ AWS_ACCESS_KEY_ID
✅ AWS_SECRET_ACCESS_KEY
✅ S3_BUCKET
✅ SUPABASE_URL
✅ SUPABASE_KEY
✅ SUPABASE_SERVICE_ROLE_KEY
✅ GEMINI_API_KEY (optional)
✅ EC2 Public IP Address
```

---

## 🛠️ Deployment Steps

### Step 1: SSH vào EC2 Instance

```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

### Step 2: Chạy Setup Script

```bash
# Download và chạy setup script
sudo yum update -y
sudo yum install -y git
git clone https://github.com/lephucchi/finance_portfolio.git
cd finance_portfolio/deployment
sudo bash setup_ec2.sh
```

**Setup script sẽ:**
- ✅ Cài Docker & Docker Compose
- ✅ Cài Nginx
- ✅ Cài AWS CLI
- ✅ Cấu hình firewall
- ✅ Tạo swap space
- ✅ Tạo file .env.template

### Step 3: Logout và Login lại

```bash
exit
ssh -i your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

### Step 4: Cấu hình Environment Files

#### 4.1. Backend Environment

```bash
cd ~/finance_portfolio/web_executor/backend
cp .env.example .env
nano .env
```

**Cập nhật các giá trị sau:**

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_actual_key
AWS_SECRET_ACCESS_KEY=your_actual_secret
AWS_DEFAULT_REGION=ap-southeast-1
S3_BUCKET=bankanalystportfolio

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# CORS - ADD YOUR EC2 PUBLIC IP
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://YOUR_EC2_IP:5173,http://YOUR_EC2_IP:8000

# Production settings
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO

# RAG Configuration
RAG_ENABLED=True
RAG_FAISS_INDEX_PATH=data/rag/vector_index.faiss
RAG_METADATA_PATH=data/rag/metadata.json
```

#### 4.2. Frontend Environment

```bash
cd ~/finance_portfolio/web_executor/frontend
cp .env.example .env
nano .env
```

**Cập nhật:**

```bash
# IMPORTANT: Update with your EC2 public IP
VITE_API_BASE_URL=http://YOUR_EC2_IP:8000/api/v1

VITE_PORT=5173
VITE_DATA_START_DATE=2025-10-18
VITE_DATA_END_DATE=2025-10-30
VITE_ENABLE_RAG_CHAT=true
```

#### 4.3. Airflow Environment

```bash
cd ~/finance_portfolio/airflow
cp .env.example .env
nano .env
```

**Cập nhật:**

```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=ap-southeast-1
S3_BUCKET=bankanalystportfolio

_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=change_this_strong_password

AIRFLOW_UID=50000
```

### Step 5: Build và Start Services

```bash
cd ~/finance_portfolio

# Build images
docker-compose build --no-cache

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### Step 6: Kiểm tra Health

```bash
# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:5173
curl http://localhost:8080/health
```

### Step 7: Verify từ Browser

Truy cập các URLs sau (thay YOUR_EC2_IP):

```
✅ Frontend: http://YOUR_EC2_IP:5173
✅ Backend API: http://YOUR_EC2_IP:8000/api/v1
✅ API Docs: http://YOUR_EC2_IP:8000/docs
✅ Airflow: http://YOUR_EC2_IP:8080 (admin/your_password)
```

---

## 🔍 Troubleshooting Common Issues

### Issue 1: CORS Error từ Frontend

**Triệu chứng:** Console error "CORS policy blocked"

**Giải pháp:**

```bash
# Edit backend .env
cd ~/finance_portfolio/web_executor/backend
nano .env

# Add your EC2 IP to ALLOWED_ORIGINS
ALLOWED_ORIGINS=http://localhost:5173,http://YOUR_EC2_IP:5173

# Restart backend
docker-compose restart backend
```

### Issue 2: Frontend không connect được Backend

**Triệu chứng:** API calls failed, network errors

**Giải pháp:**

```bash
# Edit frontend .env
cd ~/finance_portfolio/web_executor/frontend
nano .env

# Update API URL
VITE_API_BASE_URL=http://YOUR_EC2_IP:8000/api/v1

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Issue 3: Docker containers không start

**Giải pháp:**

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Check resources
docker stats
free -h
df -h

# Restart Docker
sudo systemctl restart docker
docker-compose up -d
```

### Issue 4: Security Group blocking ports

**Giải pháp:**

1. Vào AWS Console → EC2 → Security Groups
2. Tìm security group của instance
3. Edit Inbound Rules
4. Add rules cho ports: 5173, 8000, 8080

### Issue 5: Out of Memory

**Giải pháp:**

```bash
# Check memory
free -h

# Check if swap is enabled
swapon --show

# If no swap, create one
sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 📊 Monitoring Commands

### Quick Status Check

```bash
cd ~/finance_portfolio
bash deployment/monitor.sh
```

### Detailed Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f airflow-scheduler

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Container Stats

```bash
# Real-time stats
docker stats

# Container status
docker-compose ps

# System resources
htop  # or top
```

### Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:5173

# Airflow
curl http://localhost:8080/health

# Database
docker-compose exec postgres pg_isready -U airflow
```

---

## 🔄 Maintenance Tasks

### Update Code (CI/CD)

```bash
cd ~/finance_portfolio
bash deployment/deploy_production.sh
```

### Backup Database

```bash
cd ~/finance_portfolio
docker-compose exec -T postgres pg_dump -U airflow airflow > backup_$(date +%Y%m%d).sql
```

### Clean Docker Resources

```bash
# Remove old images
docker image prune -f

# Remove unused volumes (CAREFUL!)
docker volume prune -f

# Remove all stopped containers
docker container prune -f
```

### View Logs Location

```bash
# Backend logs
ls -lh ~/finance_portfolio/web_executor/backend/logs/

# Airflow logs
ls -lh ~/finance_portfolio/airflow/logs/

# Monitor script logs
tail -f ~/finance_portfolio/logs/monitor.log
```

---

## 🔐 Security Best Practices

### 1. Update Passwords

```bash
# Airflow admin password
cd ~/finance_portfolio/airflow
nano .env
# Change _AIRFLOW_WWW_USER_PASSWORD

# Restart Airflow
docker-compose restart airflow-webserver
```

### 2. Restrict SSH Access

```bash
# Edit Security Group to allow only your IP
# AWS Console → EC2 → Security Groups → Inbound Rules
# SSH (22): Change to "My IP" instead of 0.0.0.0/0
```

### 3. Enable HTTPS (Optional)

```bash
# Install Certbot (if using domain)
sudo yum install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Update frontend .env
VITE_API_BASE_URL=https://your-domain.com/api/v1
```

### 4. Rotate AWS Credentials

```bash
# Update .env files with new credentials
# Restart affected services
docker-compose restart backend airflow-scheduler
```

---

## 📝 Quick Reference

### Important Directories

```
~/finance_portfolio/                    # Project root
  ├── web_executor/backend/            # Backend API
  │   ├── .env                         # Backend config
  │   └── logs/                        # Backend logs
  ├── web_executor/frontend/           # Frontend
  │   └── .env                         # Frontend config
  ├── airflow/                         # Airflow
  │   ├── .env                         # Airflow config
  │   ├── dags/                        # Airflow DAGs
  │   └── logs/                        # Airflow logs
  ├── deployment/                      # Deployment scripts
  └── docker-compose.yml               # Docker compose config
```

### Port Mappings

```
5173  → Frontend (React)
8000  → Backend API (FastAPI)
8080  → Airflow Web UI
5432  → PostgreSQL (internal)
6379  → Redis (internal)
```

### Essential Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs
docker-compose logs -f [service_name]

# Check status
docker-compose ps

# Access container shell
docker-compose exec backend bash
```

---

## 🆘 Support & Resources

### Documentation

- Backend API Docs: `http://YOUR_EC2_IP:8000/docs`
- Project README: `~/finance_portfolio/README.md`
- Deployment Guide: `~/finance_portfolio/deployment/DEPLOYMENT_GUIDE.md`

### Logs Location

- Backend: `~/finance_portfolio/web_executor/backend/logs/`
- Airflow: `~/finance_portfolio/airflow/logs/`
- Monitor: `~/finance_portfolio/logs/monitor.log`

### Common Issues Repository

- GitHub Issues: https://github.com/lephucchi/finance_portfolio/issues
- Docker Compose Docs: https://docs.docker.com/compose/

---

## ✅ Post-Deployment Verification

Run this checklist after deployment:

```bash
# 1. Check all containers are running
docker-compose ps
# Expected: All services "Up"

# 2. Test health endpoints
curl http://localhost:8000/health
curl http://localhost:5173
curl http://localhost:8080/health
# Expected: HTTP 200 OK

# 3. Check logs for errors
docker-compose logs --tail=50 backend | grep -i error
docker-compose logs --tail=50 frontend | grep -i error
# Expected: No critical errors

# 4. Test from browser
# Visit http://YOUR_EC2_IP:5173
# Expected: Frontend loads, can make API calls

# 5. Check disk space
df -h
# Expected: Less than 80% used

# 6. Check memory
free -h
# Expected: Some free memory available

# 7. Verify AWS connectivity
docker-compose exec backend python -c "import boto3; s3=boto3.client('s3'); print(s3.list_buckets())"
# Expected: List of S3 buckets
```

---

## 🎯 Success Indicators

✅ All Docker containers show "Up" status
✅ Frontend accessible at `http://YOUR_EC2_IP:5173`
✅ Backend API docs at `http://YOUR_EC2_IP:8000/docs`
✅ Airflow UI at `http://YOUR_EC2_IP:8080`
✅ No CORS errors in browser console
✅ API calls successful from frontend
✅ Logs show no critical errors
✅ Memory usage < 80%
✅ Disk usage < 80%

---

**Last Updated:** 2025-11-06
**Version:** 1.0.0
**Maintainer:** Finance Portfolio Team
