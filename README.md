# Life Dashboard (Flask)

A minimal life dashboard with habits, journal (with heatmap), categories/subpages and files. Built with Flask 3, Bootstrap 5, Quill, Chart.js Matrix, SQLAlchemy, APScheduler.

## Features
- Habits with daily toggle and optional reminder (email/Telegram via scheduler)
- Journal with rich text and a 12‑month activity heatmap; click a date to open the entry
- Categories and subpages with file uploads
- CSRF protection enabled (Flask‑WTF)

## Run locally
1. Create `.env` with at least:
```
SECRET_KEY=dev-secret
DATABASE_URL=sqlite:///app.db
```
2. Install and run:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
flask --app app run --debug
```

## Database migrations
```
flask --app app db upgrade
```

## Deployment (free options)
- Render Free Web Service:
  - Build command: `pip install -r requirements.txt && flask --app app db upgrade`
  - Start command: `gunicorn wsgi:app`
  - Environment: set `DATABASE_URL` (Render PostgreSQL), `SECRET_KEY`, optional `MAIL_*`, `TELEGRAM_*`.
- Railway:
  - Add Python plugin. Start command: `gunicorn wsgi:app`. Add a PostgreSQL plugin and set `DATABASE_URL`.
- Fly.io/Zeet: similar; ensure port 8080/5000 mapping and use `gunicorn wsgi:app`.

CSRF is enabled globally. Forms include `{{ csrf_token() }}` and JS sends header `X-CSRFToken` from a meta tag.

## Environment variables
- SECRET_KEY: Flask secret
- DATABASE_URL: e.g. `postgresql://user:pass@host:5432/db` (auto-normalized to psycopg URL)
- MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER
- TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

## Supabase
If using Supabase Postgres, use the provided connection string for `DATABASE_URL`. Run migrations via `flask db upgrade` with the connection string set.