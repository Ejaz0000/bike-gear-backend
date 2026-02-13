# 10 - Deployment Guide

**Last Updated:** November 23, 2025

This comprehensive guide covers deploying the BikeShop Django e-commerce platform to production.

---

## 📋 Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Static & Media Files](#static--media-files)
6. [Security Checklist](#security-checklist)
7. [Server Options](#server-options)
8. [Deployment Steps](#deployment-steps)
9. [Post-Deployment](#post-deployment)
10. [Monitoring & Maintenance](#monitoring--maintenance)
11. [Troubleshooting](#troubleshooting)

---

## Deployment Overview

### Development vs Production

```
Development Environment          Production Environment
├── DEBUG = True                ├── DEBUG = False
├── SQLite database             ├── PostgreSQL/MySQL
├── Django dev server           ├── Gunicorn/uWSGI
├── No HTTPS                    ├── SSL/TLS (HTTPS)
├── Local files                 ├── Cloud storage (S3)
├── Simple settings             ├── Environment variables
└── No caching                  └── Redis/Memcached
```

### Deployment Architecture

```
User Request (HTTPS)
    ↓
Nginx (Reverse Proxy)
    ↓
Gunicorn (WSGI Server)
    ↓
Django Application
    ↓
PostgreSQL Database
    ↓
Redis Cache (Optional)
```

---

## Prerequisites

### Required Software

1. **Python 3.13+**
   ```bash
   python --version
   # Python 3.13.0
   ```

2. **pip & pipenv**
   ```bash
   pip install pipenv
   ```

3. **Database:**
   - PostgreSQL 14+ (recommended)
   - MySQL 8.0+ (alternative)

4. **Web Server:**
   - Nginx or Apache

5. **Process Manager:**
   - Gunicorn or uWSGI

### Server Requirements

**Minimum:**
- 1 CPU Core
- 2GB RAM
- 20GB Storage
- Ubuntu 20.04+ or CentOS 8+

**Recommended:**
- 2+ CPU Cores
- 4GB+ RAM
- 50GB+ Storage SSD
- Load balancer for high traffic

---

## Environment Configuration

### Step 1: Create `.env` File

**File:** `.env` (root directory)

```bash
# Django Settings
SECRET_KEY='your-super-secret-key-here-change-this-in-production'
DEBUG=False
ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com,api.yourdomain.com'

# Database Configuration
DB_ENGINE='django.db.backends.postgresql'
DB_NAME='bikeshop_db'
DB_USER='bikeshop_user'
DB_PASSWORD='strong_database_password_here'
DB_HOST='localhost'
DB_PORT='5432'

# For MySQL (alternative):
# DB_ENGINE='django.db.backends.mysql'
# DB_PORT='3306'

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS Settings
CORS_ALLOWED_ORIGINS='https://yourdomain.com,https://www.yourdomain.com'

# Media & Static Files (Production)
MEDIA_URL='https://yourbucket.s3.amazonaws.com/media/'
STATIC_URL='https://yourbucket.s3.amazonaws.com/static/'

# Email Configuration (for password reset)
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER='your-email@gmail.com'
EMAIL_HOST_PASSWORD='your-app-specific-password'
DEFAULT_FROM_EMAIL='BikeShop <noreply@yourdomain.com>'

# Optional: Redis Cache
REDIS_URL='redis://localhost:6379/1'

# Optional: AWS S3 for media files
AWS_ACCESS_KEY_ID='your-aws-access-key'
AWS_SECRET_ACCESS_KEY='your-aws-secret-key'
AWS_STORAGE_BUCKET_NAME='your-bucket-name'
AWS_S3_REGION_NAME='us-east-1'

# Optional: Sentry for error tracking
SENTRY_DSN='https://your-sentry-dsn-here'
```

**Generate SECRET_KEY:**

```python
# In Python shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

### Step 2: Update `settings.py`

**File:** `bike_shop/settings.py`

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
        'OPTIONS': {
            'charset': 'utf8mb4',
        } if 'mysql' in os.getenv('DB_ENGINE', '') else {}
    }
}

# Security Settings (Production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Static files (CSS, JavaScript, Images)
STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (User uploads)
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# Optional: AWS S3 for media storage
if os.getenv('AWS_ACCESS_KEY_ID'):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = 'public-read'

# CORS Settings
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# Email Configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '25'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

# Optional: Redis Cache
if os.getenv('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.getenv('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## Database Setup

### Option 1: PostgreSQL (Recommended)

**Install PostgreSQL:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Create Database and User:**

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE bikeshop_db;
CREATE USER bikeshop_user WITH PASSWORD 'strong_password_here';
ALTER ROLE bikeshop_user SET client_encoding TO 'utf8';
ALTER ROLE bikeshop_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE bikeshop_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE bikeshop_db TO bikeshop_user;
\q
```

**Install Python PostgreSQL Driver:**

```bash
pip install psycopg2-binary
```

---

### Option 2: MySQL

**Install MySQL:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

**Create Database and User:**

```bash
# Login to MySQL
sudo mysql -u root -p

# In MySQL shell:
CREATE DATABASE bikeshop_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bikeshop_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON bikeshop_db.* TO 'bikeshop_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Install Python MySQL Driver:**

```bash
pip install mysqlclient
```

---

## Static & Media Files

### Collect Static Files

```bash
# Run collectstatic to gather all static files
python manage.py collectstatic --noinput
```

This copies all static files from:
- `static/` directory
- App static directories
- Admin static files

To: `STATIC_ROOT` (usually `staticfiles/`)

---

### Configure Nginx to Serve Static Files

**File:** `/etc/nginx/sites-available/bikeshop`

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Logs
    access_log /var/log/nginx/bikeshop_access.log;
    error_log /var/log/nginx/bikeshop_error.log;
    
    # Max upload size
    client_max_body_size 20M;
    
    # Static files
    location /static/ {
        alias /var/www/bikeshop/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/bikeshop/media/;
        expires 30d;
        add_header Cache-Control "public";
    }
    
    # Proxy to Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable Site:**

```bash
sudo ln -s /etc/nginx/sites-available/bikeshop /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

---

### SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

---

## Security Checklist

### 1. Secret Key

```python
# ❌ NEVER commit this
SECRET_KEY = 'actual-secret-key-here'

# ✅ Use environment variable
SECRET_KEY = os.getenv('SECRET_KEY')
```

---

### 2. Debug Mode

```python
# ❌ NEVER in production
DEBUG = True

# ✅ Production setting
DEBUG = False
```

---

### 3. Allowed Hosts

```python
# ❌ Too permissive
ALLOWED_HOSTS = ['*']

# ✅ Specific domains only
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

---

### 4. Database Credentials

```python
# ❌ NEVER hardcode
DATABASES = {
    'default': {
        'PASSWORD': 'my_password_123',
    }
}

# ✅ Use environment variables
DATABASES = {
    'default': {
        'PASSWORD': os.getenv('DB_PASSWORD'),
    }
}
```

---

### 5. HTTPS Enforcement

```python
# Production settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

### 6. Security Headers

```python
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

### 7. CORS Configuration

```python
# ❌ Too permissive
CORS_ALLOW_ALL_ORIGINS = True

# ✅ Specific origins only
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]
```

---

### 8. File Permissions

```bash
# Make manage.py executable
chmod +x manage.py

# Secure media directory
chmod 755 media/
chmod 755 staticfiles/

# Secure .env file
chmod 600 .env
```

---

## Server Options

### Option 1: Gunicorn (Recommended)

**Install:**

```bash
pip install gunicorn
```

**Run:**

```bash
gunicorn bike_shop.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

**Systemd Service:**

**File:** `/etc/systemd/system/bikeshop.service`

```ini
[Unit]
Description=BikeShop Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/bikeshop
Environment="PATH=/var/www/bikeshop/venv/bin"
ExecStart=/var/www/bikeshop/venv/bin/gunicorn \
    --workers 3 \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/bikeshop/access.log \
    --error-logfile /var/log/bikeshop/error.log \
    bike_shop.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Start Service:**

```bash
sudo systemctl daemon-reload
sudo systemctl start bikeshop
sudo systemctl enable bikeshop
sudo systemctl status bikeshop
```

---

### Option 2: uWSGI

**Install:**

```bash
pip install uwsgi
```

**Configuration:**

**File:** `uwsgi.ini`

```ini
[uwsgi]
module = bike_shop.wsgi:application
master = true
processes = 4
socket = /tmp/bikeshop.sock
chmod-socket = 666
vacuum = true
die-on-term = true
```

**Run:**

```bash
uwsgi --ini uwsgi.ini
```

---

## Deployment Steps

### Step 1: Clone Repository

```bash
cd /var/www/
git clone https://github.com/yourusername/bikeshop.git bikeshop
cd bikeshop
```

---

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
# Or if using Pipenv:
pipenv install
```

---

### Step 4: Configure Environment

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with production values
nano .env
```

---

### Step 5: Run Migrations

```bash
python manage.py migrate
```

---

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

---

### Step 7: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

### Step 8: Test Application

```bash
python manage.py runserver 0.0.0.0:8000
```

Visit: `http://your-server-ip:8000`

---

### Step 9: Configure Gunicorn & Nginx

Follow sections above for Gunicorn and Nginx configuration.

---

### Step 10: Start Services

```bash
sudo systemctl start bikeshop
sudo systemctl start nginx
```

---

## Post-Deployment

### Create Initial Data

```python
# Create categories
python manage.py shell

from catalog.models import Category, Brand

# Create top-level categories
bikes = Category.objects.create(name="Bikes", slug="bikes")
accessories = Category.objects.create(name="Accessories", slug="accessories")

# Create subcategories
Category.objects.create(name="Mountain Bikes", slug="mountain-bikes", parent=bikes)
Category.objects.create(name="Road Bikes", slug="road-bikes", parent=bikes)

# Create brands
Brand.objects.create(name="Trek", slug="trek", website="https://www.trekbikes.com")
Brand.objects.create(name="Specialized", slug="specialized", website="https://www.specialized.com")
```

---

### Backup Database

```bash
# PostgreSQL backup
pg_dump -U bikeshop_user bikeshop_db > backup_$(date +%Y%m%d_%H%M%S).sql

# MySQL backup
mysqldump -u bikeshop_user -p bikeshop_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
# PostgreSQL: psql -U bikeshop_user bikeshop_db < backup.sql
# MySQL: mysql -u bikeshop_user -p bikeshop_db < backup.sql
```

---

### Automated Backups (Cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * pg_dump -U bikeshop_user bikeshop_db > /backups/bikeshop_$(date +\%Y\%m\%d).sql

# Keep only last 7 days
0 3 * * * find /backups/ -name "bikeshop_*.sql" -mtime +7 -delete
```

---

## Monitoring & Maintenance

### System Monitoring

**Check Service Status:**

```bash
sudo systemctl status bikeshop
sudo systemctl status nginx
sudo systemctl status postgresql
```

**View Logs:**

```bash
# Django logs
tail -f /var/log/bikeshop/error.log

# Nginx logs
tail -f /var/log/nginx/bikeshop_error.log

# System logs
journalctl -u bikeshop -f
```

---

### Performance Monitoring

**Install django-debug-toolbar (Development only):**

```bash
pip install django-debug-toolbar
```

**Monitor Database:**

```sql
-- PostgreSQL: Show slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

-- MySQL: Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

---

### Application Updates

```bash
# Pull latest code
cd /var/www/bikeshop
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart bikeshop
```

---

## Troubleshooting

### Issue 1: Static Files Not Loading

**Problem:** CSS/JS files return 404

**Solution:**

```bash
# 1. Check STATIC_ROOT setting
python manage.py collectstatic

# 2. Verify Nginx configuration
sudo nginx -t

# 3. Check file permissions
ls -la /var/www/bikeshop/staticfiles/

# 4. Fix permissions if needed
sudo chown -R www-data:www-data /var/www/bikeshop/staticfiles/
```

---

### Issue 2: Database Connection Error

**Problem:** `django.db.utils.OperationalError: FATAL: password authentication failed`

**Solution:**

```bash
# 1. Verify .env credentials
cat .env | grep DB_

# 2. Test database connection
psql -U bikeshop_user -d bikeshop_db -h localhost

# 3. Check pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf

# 4. Restart PostgreSQL
sudo systemctl restart postgresql
```

---

### Issue 3: 502 Bad Gateway

**Problem:** Nginx shows 502 error

**Solution:**

```bash
# 1. Check if Gunicorn is running
sudo systemctl status bikeshop

# 2. Check Gunicorn logs
sudo journalctl -u bikeshop -n 50

# 3. Test Gunicorn manually
cd /var/www/bikeshop
source venv/bin/activate
gunicorn bike_shop.wsgi:application --bind 0.0.0.0:8000

# 4. Check Nginx proxy settings
sudo nginx -t
```

---

### Issue 4: Permission Denied on Media Uploads

**Problem:** Cannot upload images

**Solution:**

```bash
# 1. Check media directory permissions
ls -la /var/www/bikeshop/media/

# 2. Fix permissions
sudo chown -R www-data:www-data /var/www/bikeshop/media/
sudo chmod -R 755 /var/www/bikeshop/media/

# 3. Create subdirectories if needed
mkdir -p /var/www/bikeshop/media/products
mkdir -p /var/www/bikeshop/media/categories
mkdir -p /var/www/bikeshop/media/brands
```

---

### Issue 5: CSRF Verification Failed

**Problem:** CSRF token missing or incorrect

**Solution:**

```python
# In settings.py
CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]

# In Nginx config
proxy_set_header X-Forwarded-Proto $scheme;
```

---

## Production Checklist

### Before Going Live

- [ ] Set `DEBUG = False`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up production database (PostgreSQL/MySQL)
- [ ] Configure HTTPS/SSL
- [ ] Set security headers
- [ ] Configure CORS properly
- [ ] Set up email backend
- [ ] Collect static files
- [ ] Create superuser account
- [ ] Test all endpoints
- [ ] Set up automated backups
- [ ] Configure monitoring
- [ ] Set up error logging
- [ ] Test file uploads
- [ ] Test payment processing (if applicable)
- [ ] Load test application
- [ ] Review security settings
- [ ] Document deployment process
- [ ] Train staff on admin interface

---

## Summary

### Key Steps

1. **Environment Setup:** Configure `.env` with production values
2. **Database:** Set up PostgreSQL or MySQL
3. **Static Files:** Collect and serve via Nginx
4. **SSL:** Configure Let's Encrypt certificates
5. **Application Server:** Set up Gunicorn with systemd
6. **Web Server:** Configure Nginx as reverse proxy
7. **Security:** Enable all security settings
8. **Monitoring:** Set up logging and monitoring
9. **Backups:** Configure automated database backups
10. **Testing:** Thoroughly test all functionality

### Production URLs

```
Main Site: https://yourdomain.com
Admin Dashboard: https://yourdomain.com/
API: https://yourdomain.com/api/
Django Admin: https://yourdomain.com/admin/
```

---

**Previous:** [09_PACKAGES_EXPLAINED.md](./09_PACKAGES_EXPLAINED.md) - Package Documentation

**Return to:** [README.md](./README.md) - Documentation Index
