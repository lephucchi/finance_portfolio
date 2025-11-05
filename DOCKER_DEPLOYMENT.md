# 🐳 Docker Deployment Guide

## 📋 Tổng quan

File `docker-compose.yml` duy nhất ở root quản lý toàn bộ hệ thống:
- **Airflow**: Data pipeline orchestration (ports: 8080)
- **Backend API**: FastAPI service (ports: 8000)
- **Frontend**: React + Express (ports: 5173)
- **PostgreSQL**: Database cho Airflow (ports: 5432)
- **Redis**: Message broker cho Celery

## 🚀 Quick Start

### 1. Chuẩn bị môi trường

```bash
# Copy và cấu hình file .env
cp airflow/.env.example airflow/.env
cp web_executor/backend/.env.example web_executor/backend/.env
cp web_executor/frontend/.env.example web_executor/frontend/.env

# Chỉnh sửa các file .env với thông tin thực tế
```

### 2. Build và chạy toàn bộ services

```bash
# Build tất cả images
docker-compose build

# Chạy tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f
```

### 3. Chạy từng nhóm services

```bash
# Chỉ chạy Airflow
docker-compose up -d postgres redis airflow-init airflow-webserver airflow-scheduler airflow-triggerer

# Chỉ chạy Web Executor
docker-compose up -d backend frontend

# Chạy tất cả
docker-compose up -d
```

## 📦 Services

| Service | Port | URL | Mô tả |
|---------|------|-----|-------|
| Frontend | 5173 | http://localhost:5173 | React Web UI |
| Backend API | 8000 | http://localhost:8000 | FastAPI REST API |
| Airflow Web | 8080 | http://localhost:8080 | Airflow UI (admin/admin123) |
| PostgreSQL | 5432 | localhost:5432 | Database |

## 🔧 Quản lý Services

### Kiểm tra trạng thái

```bash
# Xem tất cả services
docker-compose ps

# Xem logs của service cụ thể
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f airflow-webserver
```

### Restart services

```bash
# Restart một service
docker-compose restart backend

# Restart tất cả
docker-compose restart
```

### Stop và remove

```bash
# Stop tất cả
docker-compose stop

# Stop và xóa containers
docker-compose down

# Xóa cả volumes (CẢNH BÁO: mất data)
docker-compose down -v
```

## 🔄 Update và Rebuild

```bash
# Rebuild sau khi thay đổi code
docker-compose build backend
docker-compose build frontend

# Rebuild và restart
docker-compose up -d --build backend frontend
```

## 🐛 Troubleshooting

### Backend không kết nối được

```bash
# Kiểm tra logs
docker-compose logs backend

# Vào container để debug
docker-compose exec backend bash
```

### Frontend không load được

```bash
# Kiểm tra logs
docker-compose logs frontend

# Rebuild với no-cache
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Airflow không khởi động

```bash
# Xem logs init
docker-compose logs airflow-init

# Reset database (CẢNH BÁO: mất data)
docker-compose down -v
docker-compose up -d
```

## 🌐 Deploy lên EC2 Ubuntu

### 1. Chuẩn bị EC2 Instance

```bash
# SSH vào EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Cài Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu

# Logout và login lại để apply group
exit
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. Deploy ứng dụng

```bash
# Clone repository
git clone https://github.com/lephucchi/finance_portfolio.git
cd finance_portfolio

# Cấu hình .env files
nano airflow/.env
nano web_executor/backend/.env
nano web_executor/frontend/.env

# Build và chạy
docker-compose build
docker-compose up -d

# Kiểm tra
docker-compose ps
docker-compose logs -f
```

### 3. Cấu hình Security Groups

Mở các ports trên AWS Security Group:
- **5173**: Frontend
- **8000**: Backend API
- **8080**: Airflow Web UI
- **22**: SSH (chỉ từ IP của bạn)

### 4. Setup Domain và SSL (Optional)

```bash
# Cài Nginx làm reverse proxy
sudo apt install -y nginx certbot python3-certbot-nginx

# Cấu hình Nginx
sudo nano /etc/nginx/sites-available/finance-portfolio

# Cài SSL với Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoring

### Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:5173/health

# Airflow
curl http://localhost:8080/health
```

### Resource Usage

```bash
# Xem tài nguyên sử dụng
docker stats

# Xem disk usage
docker system df
```

## 🔐 Security Best Practices

1. **Không commit file .env** vào Git
2. **Thay đổi mật khẩu mặc định** trong production
3. **Sử dụng secrets** cho thông tin nhạy cảm
4. **Giới hạn ports** chỉ mở những gì cần thiết
5. **Update images** thường xuyên cho security patches

## 📝 Environment Variables

### Airflow (.env)
- `AWS_ACCESS_KEY_ID`: AWS credentials
- `AWS_SECRET_ACCESS_KEY`: AWS credentials
- `_AIRFLOW_WWW_USER_USERNAME`: Airflow admin username
- `_AIRFLOW_WWW_USER_PASSWORD`: Airflow admin password

### Backend (.env)
- `AWS_REGION`: AWS region
- `ATHENA_DATABASE`: Database name
- `SUPABASE_URL`: Supabase URL
- `SUPABASE_KEY`: Supabase API key

### Frontend (.env)
- `VITE_API_BASE_URL`: Backend API URL
- `NODE_ENV`: Environment (production/development)

## 🎯 Production Checklist

- [ ] Cấu hình tất cả .env files
- [ ] Thay đổi mật khẩu mặc định
- [ ] Setup backup cho PostgreSQL
- [ ] Cấu hình monitoring và alerting
- [ ] Setup logs aggregation
- [ ] Configure SSL/TLS
- [ ] Setup CI/CD pipeline
- [ ] Test disaster recovery

## 📚 Tài liệu tham khảo

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Airflow Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
