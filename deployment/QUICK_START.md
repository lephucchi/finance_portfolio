# 🚀 Quick Start - EC2 Deployment

## Trước khi bắt đầu

Chuẩn bị sẵn:
- ✅ EC2 Public IP: `_________________`
- ✅ AWS Access Key: `_________________`
- ✅ AWS Secret Key: `_________________`
- ✅ Supabase URL: `_________________`
- ✅ Supabase Keys: `_________________`

## Bước 1: SSH vào EC2

```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_IP
```

## Bước 2: Setup cơ bản

```bash
sudo yum update -y
sudo yum install -y git
git clone https://github.com/lephucchi/finance_portfolio.git
cd finance_portfolio/deployment
sudo bash setup_ec2.sh
```

Logout và login lại để apply Docker permissions.

## Bước 3: Cấu hình Environment

### Backend
```bash
cd ~/finance_portfolio/web_executor/backend
cp .env.example .env
nano .env
```

**CẬP NHẬT:**
```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
ALLOWED_ORIGINS=http://YOUR_EC2_IP:5173,http://YOUR_EC2_IP:8000
DEBUG=False
ENVIRONMENT=production
```

### Frontend
```bash
cd ~/finance_portfolio/web_executor/frontend
cp .env.example .env
nano .env
```

**CẬP NHẬT:**
```bash
VITE_API_BASE_URL=http://YOUR_EC2_IP:8000/api/v1
VITE_ENABLE_RAG_CHAT=true
```

### Airflow
```bash
cd ~/finance_portfolio/airflow
cp .env.example .env
nano .env
```

**CẬP NHẬT:**
```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
_AIRFLOW_WWW_USER_PASSWORD=strong_password
```

## Bước 4: Deploy

```bash
cd ~/finance_portfolio
docker-compose build
docker-compose up -d
```

## Bước 5: Verify

```bash
# Check status
docker-compose ps

# Check health
curl http://localhost:8000/health
curl http://localhost:5173

# View logs
docker-compose logs -f backend
```

## Bước 6: Test từ Browser

Mở trình duyệt và truy cập:

- **Frontend:** `http://YOUR_EC2_IP:5173`
- **API Docs:** `http://YOUR_EC2_IP:8000/docs`
- **Airflow:** `http://YOUR_EC2_IP:8080`

## ⚠️ Troubleshooting Nhanh

### CORS Error?
```bash
# Kiểm tra backend .env
cat ~/finance_portfolio/web_executor/backend/.env | grep ALLOWED_ORIGINS
# Phải có: http://YOUR_EC2_IP:5173
```

### Frontend không connect Backend?
```bash
# Kiểm tra frontend .env
cat ~/finance_portfolio/web_executor/frontend/.env | grep VITE_API_BASE_URL
# Phải là: http://YOUR_EC2_IP:8000/api/v1
```

### Containers không start?
```bash
docker-compose logs backend
docker-compose logs frontend
# Xem logs để tìm lỗi
```

## 📊 Monitoring

```bash
# Quick health check
bash ~/finance_portfolio/deployment/monitor.sh

# Container stats
docker stats

# Logs
docker-compose logs -f
```

## 🔄 Update Code

```bash
cd ~/finance_portfolio
git pull origin main
docker-compose build
docker-compose up -d
```

## 🆘 Emergency

```bash
# Stop all
docker-compose down

# Start all
docker-compose up -d

# Restart specific service
docker-compose restart backend
```

---

**📚 Chi tiết đầy đủ:** Xem `EC2_DEPLOYMENT_CHECKLIST.md`
