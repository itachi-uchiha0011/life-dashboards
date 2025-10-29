# syntax=docker/dockerfile:1
# Optimized for Render.com deployment
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_APP=wsgi:app

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

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/instance /app/uploads /app/static/uploads && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose a fixed port (Render sets PORT at runtime)
# EXPOSE cannot take env vars during build, so use a number
EXPOSE 10000

# Health check endpoint that does not require DB
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import os,requests; requests.get(f'http://localhost:{os.environ.get(\"PORT\", 10000)}/status', timeout=10)" || exit 1

# Copy entrypoint and make executable
COPY --chown=appuser:appuser docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Start via entrypoint that runs migrations first
CMD ["/app/docker-entrypoint.sh"]