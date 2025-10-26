# psycopg2-binary Build Error Fix

## 🔧 **Problem:**
```
ERROR: Failed building wheel for psycopg2-binary
error: command '/usr/bin/gcc' failed with exit code 1
```

## ✅ **Solutions:**

### **Solution 1: Fixed Dockerfile (Recommended)**
Updated Dockerfile with all required system dependencies:

```dockerfile
# Install system dependencies for psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    g++ \
    make \
    libc6-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean
```

### **Solution 2: Alternative Requirements**
If psycopg2-binary still fails, use `requirements-alternative.txt`:

```bash
# Use psycopg2 instead of psycopg2-binary
psycopg2==2.9.9
```

### **Solution 3: SQLite for Development**
For development/testing, use `requirements-sqlite.txt`:

```bash
# No PostgreSQL dependencies
# Uses SQLite database
```

## 🚀 **Deployment Options:**

### **Option 1: PostgreSQL (Production)**
```bash
# Use fixed Dockerfile
docker build -t life-dashboards:latest .

# Or use Dockerfile.render
docker build -f Dockerfile.render -t life-dashboards:latest .
```

### **Option 2: SQLite (Development)**
```bash
# Use SQLite Dockerfile
docker build -f Dockerfile.sqlite -t life-dashboards:dev .
```

### **Option 3: Alternative PostgreSQL**
```bash
# Use alternative requirements
cp requirements-alternative.txt requirements.txt
docker build -t life-dashboards:alt .
```

## 📋 **Files Created:**

1. **Dockerfile** - Fixed with all dependencies
2. **Dockerfile.render** - Fixed for Render.com
3. **Dockerfile.sqlite** - SQLite-only version
4. **requirements-alternative.txt** - psycopg2 instead of psycopg2-binary
5. **requirements-sqlite.txt** - No PostgreSQL dependencies

## 🔍 **System Dependencies Added:**

- `libpq-dev` - PostgreSQL development headers
- `gcc` - C compiler
- `g++` - C++ compiler
- `make` - Build tool
- `libc6-dev` - C library development files
- `libffi-dev` - Foreign Function Interface library

## ⚡ **Quick Fix Commands:**

### **For Production (PostgreSQL):**
```bash
# Use fixed Dockerfile
docker build -t life-dashboards:latest .
```

### **For Development (SQLite):**
```bash
# Use SQLite version
docker build -f Dockerfile.sqlite -t life-dashboards:dev .
```

### **For Render.com:**
```bash
# Use Dockerfile.render (already fixed)
docker build -f Dockerfile.render -t life-dashboards:render .
```

## 🎯 **Recommended Approach:**

1. **Try fixed Dockerfile first** - Should work now
2. **If still fails** - Use requirements-alternative.txt
3. **For development** - Use Dockerfile.sqlite
4. **For Render.com** - Use Dockerfile.render

## ✅ **Expected Result:**
All Docker builds should now complete successfully without psycopg2-binary errors!