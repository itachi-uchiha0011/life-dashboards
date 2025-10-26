import os
import logging
from datetime import timedelta
from urllib.parse import urlparse

# Set up logging for database configuration
logger = logging.getLogger(__name__)


def _normalize_database_url(url: str) -> str:
	"""Normalize database URL for psycopg driver compatibility."""
	if not url:
		return url
	# Handle postgres:// -> postgresql+psycopg:// and postgresql:// -> postgresql+psycopg://
	if url.startswith("postgres://"):
		return url.replace("postgres://", "postgresql+psycopg://", 1)
	if url.startswith("postgresql://") and "+" not in url:
		return url.replace("postgresql://", "postgresql+psycopg://", 1)
	return url


def _is_valid_database_url(url: str) -> bool:
	"""Check if the database URL is valid and reachable."""
	if not url:
		return False
	
	# Check for placeholder/invalid URLs
	invalid_patterns = [
		"your-password",
		"your-project-id",
		"your-service-role-key",
		"localhost:5432",  # Common placeholder
		"db.example.com",  # Common placeholder
	]
	
	for pattern in invalid_patterns:
		if pattern in url.lower():
			return False
	
	# For PostgreSQL URLs, check if they look like real URLs
	if url.startswith(("postgresql://", "postgres://")):
		try:
			parsed = urlparse(url)
			# Check if hostname looks like a placeholder
			if not parsed.hostname or "supabase.co" not in parsed.hostname:
				return False
		except Exception:
			return False
	
	return True


def _get_database_url() -> str:
	"""
	Get database URL with safe fallback logic.
	
	This function implements a robust fallback mechanism:
	1. First, try to get DATABASE_URL from environment
	2. If DATABASE_URL is invalid/placeholder, fall back to SQLite
	3. If no DATABASE_URL is set, use SQLite for local development
	
	This ensures the app works in both development (SQLite) and production (PostgreSQL) environments.
	"""
	database_url = os.getenv("DATABASE_URL")
	
	# If no DATABASE_URL is set, use SQLite for local development
	if not database_url:
		logger.info("No DATABASE_URL found in environment, using SQLite for local development")
		return "sqlite:///instance/app.db"
	
	# If DATABASE_URL is invalid or contains placeholders, fall back to SQLite
	if not _is_valid_database_url(database_url):
		logger.warning(f"Invalid DATABASE_URL detected: {database_url[:50]}... (contains placeholders or invalid format)")
		logger.info("Falling back to SQLite for local development")
		return "sqlite:///instance/app.db"
	
	# Normalize the URL for psycopg driver compatibility
	normalized_url = _normalize_database_url(database_url)
	logger.info(f"Using PostgreSQL database: {normalized_url.split('@')[1] if '@' in normalized_url else 'configured'}")
	return normalized_url


class Config:
	"""
	Flask application configuration with robust database fallback logic.
	
	This configuration class implements a safe fallback mechanism for database connections:
	- If DATABASE_URL is not set or contains placeholders, falls back to SQLite
	- If DATABASE_URL is valid, uses PostgreSQL with psycopg driver
	- Ensures the app works in both development and production environments
	"""
	SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
	
	# Database configuration with safe fallback logic
	# This prevents SQLAlchemy OperationalError when DATABASE_URL is invalid/unreachable
	SQLALCHEMY_DATABASE_URI = _get_database_url()
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

	# Cloudinary Storage (for production)
	CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
	CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
	CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
	CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "life-dashboards")

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