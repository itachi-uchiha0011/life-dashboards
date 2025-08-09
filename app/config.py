import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx", "ppt", "pptx", "txt"}

    # Auth
    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    # Email
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # Scheduler
    SCHEDULER_API_ENABLED = False
    JOBS_TIMEZONE = os.getenv("JOBS_TIMEZONE", "UTC")