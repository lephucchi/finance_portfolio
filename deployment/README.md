# 🚀 Deployment Files

This directory contains all deployment and operational scripts for Finance Portfolio.

## 📁 Files Overview

| File | Purpose | Usage |
|------|---------|-------|
| **setup_ec2.sh** | Initial EC2 setup | `sudo bash setup_ec2.sh` |
| **deploy_production.sh** | Production deployment | `bash deploy_production.sh` |
| **monitor.sh** | Health monitoring | `bash monitor.sh` |
| **maintenance.sh** | System maintenance | `bash maintenance.sh` |
| **nginx.conf** | Nginx configuration | Copy to `/etc/nginx/sites-available/` |
| **DEPLOYMENT_GUIDE.md** | Complete deployment guide | Read for instructions |

## 🛠️ Quick Start

### 1. Initial EC2 Setup

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Copy and run setup script
sudo bash setup_ec2.sh

# Logout and login to apply docker group
exit
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. Deploy Application

```bash
# Clone repository
git clone https://github.com/lephucchi/finance_portfolio.git
cd finance_portfolio

# Configure environment
cp airflow/.env.example airflow/.env
cp web_executor/backend/.env.example web_executor/backend/.env
cp web_executor/frontend/.env.example web_executor/frontend/.env

# Edit .env files with your credentials
nano airflow/.env
nano web_executor/backend/.env
nano web_executor/frontend/.env

# Deploy
bash deployment/deploy_production.sh
```

### 3. Configure Nginx (Optional)

```bash
# Copy config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/finance-portfolio

# Edit domain
sudo nano /etc/nginx/sites-available/finance-portfolio

# Enable site
sudo ln -s /etc/nginx/sites-available/finance-portfolio /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and reload
sudo nginx -t
sudo systemctl reload nginx

# Setup SSL
sudo certbot --nginx -d your-domain.com
```

### 4. Setup Monitoring

```bash
# Make scripts executable
chmod +x deployment/monitor.sh
chmod +x deployment/maintenance.sh

# Run monitoring
bash deployment/monitor.sh

# Schedule monitoring (every 5 minutes)
crontab -e
# Add: */5 * * * * /home/ubuntu/finance_portfolio/deployment/monitor.sh

# Schedule maintenance (weekly, Sunday 2 AM)
# Add: 0 2 * * 0 /home/ubuntu/finance_portfolio/deployment/maintenance.sh
```

## 📋 Deployment Checklist

Before deploying:

- [ ] EC2 instance launched (t2.large recommended)
- [ ] Security groups configured (ports 22, 80, 443, 5173, 8000, 8080)
- [ ] All .env files configured
- [ ] AWS credentials valid
- [ ] Domain DNS configured (if using custom domain)
- [ ] SSL certificate ready (optional)

After deploying:

- [ ] All services running (`docker-compose ps`)
- [ ] Health checks passing (`curl http://localhost:8000/health`)
- [ ] Logs clean (`docker-compose logs -f`)
- [ ] Monitoring working (`bash deployment/monitor.sh`)
- [ ] Backups scheduled
- [ ] CI/CD pipeline tested

## 🔄 Common Operations

### View Service Status

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f airflow-scheduler
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Update Deployment

```bash
cd ~/finance_portfolio
git pull origin main
docker-compose build
docker-compose up -d --force-recreate
```

### Rollback

```bash
bash deployment/deploy_production.sh rollback <timestamp>
```

### Run Maintenance

```bash
bash deployment/maintenance.sh
```

### Check Health

```bash
bash deployment/monitor.sh
```

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs backend

# Check disk space
df -h

# Restart
docker-compose restart backend
```

### Out of memory

```bash
# Check memory
free -h

# Restart services
docker-compose restart

# Consider upgrading instance
```

### Port conflicts

```bash
# Find process
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### SSL issues

```bash
# Renew certificate
sudo certbot renew

# Check expiration
sudo certbot certificates
```

## 📞 Support

For detailed instructions, see: **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

Issues? Check logs and monitoring first:
```bash
bash deployment/monitor.sh
docker-compose logs -f
```

---

**Last Updated**: November 5, 2025
