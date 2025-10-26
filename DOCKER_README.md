# Docker Setup for Life Dashboards

This document explains how to use Docker with the Life Dashboards application.

## 🐳 Docker Files

- `Dockerfile` - Production-optimized multi-stage build
- `Dockerfile.dev` - Development environment
- `docker-compose.yml` - Complete stack with database
- `.dockerignore` - Excludes unnecessary files from build

## 🚀 Quick Start

### Production Deployment

```bash
# Build the production image
docker build -t life-dashboards:latest .

# Run with environment variables
docker run -d \
  -p 8080:8080 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e SECRET_KEY="your-secret-key" \
  life-dashboards:latest
```

### Development with Docker Compose

```bash
# Start the complete stack (app + database + redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the stack
docker-compose down
```

### Development Only

```bash
# Build development image
docker build -f Dockerfile.dev -t life-dashboards:dev .

# Run development container
docker run -p 5000:5000 \
  -e FLASK_ENV=development \
  -v $(pwd):/app \
  life-dashboards:dev
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///instance/app.db` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `FLASK_ENV` | Flask environment | `production` |
| `PORT` | Port to run on | `8080` |

## 📦 Docker Features

### Production Dockerfile
- ✅ **Multi-stage build** - Smaller final image
- ✅ **Non-root user** - Security best practice
- ✅ **Health checks** - Container health monitoring
- ✅ **Optimized layers** - Faster builds and smaller images
- ✅ **Security hardened** - Minimal attack surface

### Development Dockerfile
- ✅ **Hot reload** - Code changes reflect immediately
- ✅ **Debug mode** - Full debugging capabilities
- ✅ **Volume mounting** - Live code editing

## 🏗️ Build Process

1. **Builder Stage**: Installs dependencies and builds packages
2. **Production Stage**: Copies only necessary files and runs app
3. **Security**: Runs as non-root user
4. **Health**: Includes health check endpoint

## 🔍 Health Check

The application includes a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "message": "Life Dashboards is running"
}
```

## 📁 File Structure

```
├── Dockerfile              # Production build
├── Dockerfile.dev          # Development build
├── docker-compose.yml      # Complete stack
├── .dockerignore           # Build exclusions
└── DOCKER_README.md        # This file
```

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port mapping
   docker run -p 8081:8080 life-dashboards:latest
   ```

2. **Database connection issues**
   ```bash
   # Check database URL format
   echo $DATABASE_URL
   # Should be: postgresql://user:pass@host:port/dbname
   ```

3. **Permission issues**
   ```bash
   # Fix uploads directory permissions
   docker exec -it <container_id> chown -R appuser:appuser /app/uploads
   ```

### Debugging

```bash
# Enter container shell
docker exec -it <container_id> /bin/bash

# View application logs
docker logs <container_id>

# Check health status
curl http://localhost:8080/health
```

## 🔄 Updates

To update the application:

```bash
# Rebuild image
docker build -t life-dashboards:latest .

# Restart container
docker stop <container_id>
docker run -d [same options as before] life-dashboards:latest
```

## 📊 Performance

- **Image size**: ~200MB (optimized)
- **Startup time**: ~10-15 seconds
- **Memory usage**: ~100-200MB
- **CPU usage**: Low (idle state)