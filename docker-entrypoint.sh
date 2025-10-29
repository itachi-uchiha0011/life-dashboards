#!/bin/sh
set -e

# Default values
: "${PORT:=8080}"

echo "[entrypoint] Waiting for database and running migrations..."

# Retry loop for migrations to wait for DB readiness
MAX_RETRIES=30
SLEEP_SECONDS=2
COUNT=0

until flask db upgrade; do
  COUNT=$((COUNT+1))
  if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
    echo "[entrypoint] Migration failed after ${MAX_RETRIES} attempts. Exiting."
    exit 1
  fi
  echo "[entrypoint] Migration attempt ${COUNT} failed. Retrying in ${SLEEP_SECONDS}s..."
  sleep "$SLEEP_SECONDS"
done

echo "[entrypoint] Migrations applied. Starting app on port ${PORT}..."
exec gunicorn --bind 0.0.0.0:"${PORT}" --workers 2 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 wsgi:app
