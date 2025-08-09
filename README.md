# Life Dashboard

Full-stack Flask app: user auth, habits, journal with heatmap, categories/subpages with rich text and file uploads, reminders, and exports.

## Quickstart

1. Create and fill `.env` from `.env.example`.
2. Install deps:

```
pip install -r requirements.txt
```

3. Initialize DB:

```
flask db init
flask db migrate -m "init"
flask db upgrade
```

4. Run:

```
flask run --host 0.0.0.0 --port 5000
```

Open http://localhost:5000

## Notes
- Default DB is SQLite. Set `DATABASE_URL` for Postgres.
- Uploads go to `UPLOAD_FOLDER`.
- Heatmap uses Chart.js Matrix plugin.
- Rich text uses Quill; content is stored as HTML.
- Reminders use APScheduler. Configure email/Telegram in `.env`.