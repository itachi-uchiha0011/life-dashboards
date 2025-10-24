import os
from datetime import timedelta


def _normalize_database_url(url: str) -> str:
	if not url:
		return url
	# Handle postgres:// -> postgresql+psycopg:// and postgresql:// -> postgresql+psycopg://
	if url.startswith("postgres://"):
		return url.replace("postgres://", "postgresql+psycopg://", 1)
	if url.startswith("postgresql://") and "+" not in url:
		return url.replace("postgresql://", "postgresql+psycopg://", 1)
	return url


class Config:
	SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
	SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///app.db"))
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Uploads (local fallback, avoid for prod)
	UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
	MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
	ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx", "ppt", "pptx", "txt"}

	# Supabase Storage
	SUPABASE_URL = os.getenv("SUPABASE_URL", "")
	SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
	SUPABASE_FILES_BUCKET = os.getenv("SUPABASE_FILES_BUCKET", "files")
	SUPABASE_AVATARS_BUCKET = os.getenv("SUPABASE_AVATARS_BUCKET", "avatars")

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

	# Google Drive Integration
	GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
	GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
	GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/auth/google/callback")
	GOOGLE_DRIVE_SCOPES = [
		"https://www.googleapis.com/auth/drive.file",
		"https://www.googleapis.com/auth/drive.metadata.readonly"
	]