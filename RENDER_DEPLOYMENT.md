# Render.com Deployment Guide

## 🚀 Quick Deployment Steps

### 1. **Prepare Your Repository**
```bash
# Make sure these files are in your repo:
- Dockerfile (or Dockerfile.render)
- requirements.txt
- .env.production
- wsgi.py
- app/ directory
```

### 2. **Create Render.com Service**

#### **Option A: Docker Deployment (Recommended)**
1. Go to [Render.com Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `life-dashboards`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `Dockerfile.render` (or `Dockerfile`)
   - **Port**: `10000` (Render.com will set PORT env var)

#### **Option B: Python Deployment**
1. Go to [Render.com Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `life-dashboards`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`

### 3. **Environment Variables**
Set these in Render.com dashboard:

#### **Required Variables:**
```
FLASK_APP=wsgi:app
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
PORT=10000
```

#### **Database (Auto-provided by Render):**
```
DATABASE_URL=postgresql://... (Render provides this)
```

#### **Optional Variables:**
```
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=25165824
JOBS_TIMEZONE=UTC
```

### 4. **Database Setup**
1. In Render.com dashboard, go to your service
2. Click "Add Database" → "PostgreSQL"
3. Name it `life-dashboards-db`
4. Render will automatically set `DATABASE_URL`

### 5. **Deploy**
1. Click "Deploy" in Render.com dashboard
2. Wait for build to complete
3. Your app will be available at `https://your-app-name.onrender.com`

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **Build Fails:**
```bash
# Check requirements.txt has no recursive references
# Make sure all packages are listed directly
```

#### **Database Connection Error:**
```bash
# Check DATABASE_URL is set correctly
# Ensure PostgreSQL service is running
```

#### **Port Issues:**
```bash
# Make sure your app uses PORT environment variable
# Render.com sets PORT=10000 automatically
```

#### **Static Files Not Loading:**
```bash
# Check UPLOAD_FOLDER path
# Ensure static files are in correct directory
```

### **Debug Commands:**
```bash
# Check logs in Render.com dashboard
# Look for error messages in build logs
# Verify environment variables are set
```

## 📁 **File Structure for Render.com**

```
your-repo/
├── Dockerfile.render          # Render-optimized Dockerfile
├── requirements.txt           # Python dependencies
├── .env.production           # Production environment variables
├── wsgi.py                   # WSGI entry point
├── app/                      # Your Flask app
│   ├── __init__.py
│   ├── models.py
│   └── ...
├── migrations/               # Database migrations
└── static/                   # Static files
```

## ⚡ **Performance Tips**

1. **Use Dockerfile.render** - Optimized for Render.com
2. **Set proper PORT** - Use `$PORT` environment variable
3. **Database migrations** - Run automatically on startup
4. **Static files** - Serve from correct directory
5. **Environment variables** - Set all required vars

## 🔄 **Updates**

To update your app:
1. Push changes to GitHub
2. Render.com will automatically redeploy
3. Check logs for any issues

## 📊 **Monitoring**

- **Logs**: Available in Render.com dashboard
- **Health Check**: `/health` endpoint
- **Database**: PostgreSQL dashboard
- **Performance**: Render.com metrics

## 🆘 **Support**

If you face issues:
1. Check Render.com logs
2. Verify environment variables
3. Test locally with Docker
4. Check database connection