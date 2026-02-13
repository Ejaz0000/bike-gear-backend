# Quick Vercel Deployment Guide

## ✅ What's Been Configured

Your Django project is now ready for Vercel deployment with:

- ✅ `vercel.json` - Serverless configuration
- ✅ `build_files.sh` - Build script for static files
- ✅ WhiteNoise - Static file serving
- ✅ PostgreSQL support via `dj-database-url`
- ✅ Environment-aware settings (dev/prod)
- ✅ CORS and CSRF configured for production
- ✅ `.vercelignore` - Excludes unnecessary files
- ✅ `requirements.txt` - Updated with all dependencies

## 🚀 Deploy to Vercel (5 Steps)

### Step 1: Install Vercel CLI
```bash
npm i -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Deploy
```bash
vercel
```

### Step 4: Set Up Database

**Option A: Vercel Postgres (Easiest)**
1. Go to your Vercel project dashboard
2. Click "Storage" tab
3. Create a Postgres database
4. Environment variables are auto-added

**Option B: External PostgreSQL (Neon, Supabase, etc.)**
Add these environment variables in Vercel dashboard:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Step 5: Set Environment Variables

In your Vercel project dashboard, add:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
FRONTEND_URL=https://your-frontend.vercel.app
```

## 🔄 Deploy to Production
```bash
vercel --prod
```

## 📝 Important Notes

1. **Database**: SQLite won't work on Vercel - must use PostgreSQL
2. **Migrations**: Run after deployment:
   ```bash
   # Use Vercel CLI or add as post-deploy script
   python manage.py migrate
   python manage.py createsuperuser
   ```
3. **Media Files**: For user uploads, consider:
   - Vercel Blob Storage
   - AWS S3
   - Cloudinary

4. **CORS**: Update your frontend URL in Vercel environment variables

## 🐛 Troubleshooting

### View Logs
```bash
vercel logs
```

### Redeploy
```bash
vercel --prod
```

### Check Build Status
Visit: https://vercel.com/dashboard

## 📚 Full Documentation

See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed deployment guide.

## 🔗 Next Steps

1. ✅ Deploy to Vercel
2. ✅ Set up PostgreSQL database
3. ✅ Run migrations
4. ✅ Create superuser
5. ✅ Update frontend API URL
6. ✅ Test all endpoints
