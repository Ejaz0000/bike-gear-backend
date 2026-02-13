# Vercel Deployment Guide

## Prerequisites
1. A Vercel account (https://vercel.com)
2. Vercel CLI installed: `npm i -g vercel`
3. A PostgreSQL database (recommended: Neon, Supabase, or Vercel Postgres)

## Environment Variables Setup

In your Vercel project dashboard, add these environment variables:

```
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=.vercel.app
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432
FRONTEND_URL=https://your-frontend.vercel.app
```

## Deployment Steps

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy to Vercel
```bash
vercel
```

Follow the prompts:
- Set up and deploy? Yes
- Which scope? Select your account
- Link to existing project? No
- Project name? (accept default or enter custom name)
- In which directory is your code located? ./

### 4. Run Database Migrations

After deployment, you need to run migrations. Use Vercel CLI:

```bash
vercel env pull .env.production
```

Then SSH into your project or use a one-off command:
```bash
python manage.py migrate
python manage.py createsuperuser
```

**Note:** For Vercel, you'll need to set up a production database. SQLite won't work on Vercel's serverless environment.

### 5. Deploy to Production
```bash
vercel --prod
```

## Database Setup for Vercel

Since Vercel uses serverless functions, you need a managed PostgreSQL database:

### Option 1: Vercel Postgres (Recommended)
1. Go to your Vercel project dashboard
2. Go to Storage tab
3. Create a Postgres database
4. Environment variables will be automatically added

### Option 2: External PostgreSQL (Neon, Supabase, etc.)
1. Create a PostgreSQL database
2. Update `settings.py` to use PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

3. Add environment variables to Vercel

## Static Files

Static files are handled by WhiteNoise. The build process automatically collects static files.

## Media Files

For media files (user uploads), consider using:
- **Vercel Blob Storage** (recommended)
- **AWS S3**
- **Cloudinary**
- **Google Cloud Storage**

Update Django settings to use cloud storage for media files in production.

## CORS Configuration

Update `CORS_ALLOWED_ORIGINS` in settings.py with your frontend URL:

```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.vercel.app",
]
```

## Troubleshooting

### Build Fails
- Check the build logs in Vercel dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### Database Connection Issues
- Check environment variables are set correctly
- Ensure database allows connections from Vercel IPs
- Verify database credentials

### Static Files Not Loading
- Run `python manage.py collectstatic` locally to test
- Check STATIC_ROOT and STATIC_URL settings
- Ensure WhiteNoise middleware is properly configured

## Post-Deployment

1. Test all API endpoints
2. Create admin user via Django admin
3. Update frontend API URL to point to Vercel deployment
4. Monitor logs via `vercel logs`

## Useful Commands

```bash
# View deployment logs
vercel logs

# List deployments
vercel ls

# Remove deployment
vercel rm [deployment-url]

# Set environment variable
vercel env add SECRET_KEY

# Pull environment variables
vercel env pull
```
