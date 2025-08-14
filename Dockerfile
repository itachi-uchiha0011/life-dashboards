# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# System deps (optional): libpq for psycopg if needed
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8080

# Run DB migrations then start gunicorn with a single worker (to avoid duplicate schedulers)
CMD ["sh", "-c", "flask --app app db upgrade && exec gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:app"]