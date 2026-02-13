# Render Deployment Guide for Django Project

## Quick Start

### 1. Create Render Account
Sign up at [https://render.com](https://render.com)

### 2. Deploy via Dashboard

#### Option A: Using render.yaml (Recommended)
1. Go to Render Dashboard
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Click "Apply" to create services

#### Option B: Manual Setup
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: bike-gear-backend
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn bike_shop.wsgi:application`
   - **Plan**: Free

### 3. Create PostgreSQL Database
1. Go to Dashboard → "New" → "PostgreSQL"
2. Name: bike-gear-db
3. Plan: Free
4. Click "Create Database"

### 4. Set Environment Variables
In your Web Service settings, add:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=<automatically set from database>
FRONTEND_URL=https://your-frontend.onrender.com
```

To generate SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Connect Database to Web Service
1. Go to Web Service → "Environment"
2. Add environment variable from database:
   - Key: `DATABASE_URL`
   - Value: Select your PostgreSQL database

### 6. Deploy
Render will automatically deploy. Migrations run during build.

## Files Configured

- ✅ `render.yaml` - Blueprint configuration
- ✅ `build.sh` - Build script (installs deps, collects static, runs migrations)
- ✅ `requirements.txt` - Python dependencies (includes gunicorn)
- ✅ `settings.py` - Configured for Render environment

## Features

- ✅ PostgreSQL database included
- ✅ Automatic migrations on deploy
- ✅ WhiteNoise for static files
- ✅ Gunicorn WSGI server
- ✅ Auto-deploy on git push
- ✅ Free tier available

## CORS Configuration

Update `FRONTEND_URL` environment variable with your frontend URL.

## Monitoring

- View logs: Dashboard → Your service → "Logs"
- View metrics: Dashboard → Your service → "Metrics"

## Custom Domain (Optional)

1. Go to service settings → "Custom Domain"
2. Add your domain
3. Update DNS records as instructed

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify `build.sh` has execute permissions: `chmod +x build.sh`

### Database Connection Issues
- Ensure DATABASE_URL is set correctly
- Check database is in same region as web service

### Static Files Not Loading
- Verify `python manage.py collectstatic` runs in build.sh
- Check STATIC_ROOT and STATIC_URL settings

## Cost

- Free tier: Web Service + PostgreSQL database (with limitations)
- Check [Render Pricing](https://render.com/pricing) for details

## Post-Deployment

1. Create superuser (via Render Shell):
   ```bash
   python manage.py createsuperuser
   ```

2. Test API endpoints

3. Update frontend API URL

## Useful Commands

Access Render Shell:
- Dashboard → Your service → "Shell"
- Run Django commands: `python manage.py <command>`
