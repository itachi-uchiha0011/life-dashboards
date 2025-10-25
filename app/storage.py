import io
import uuid
import requests
import os
from typing import Optional, Tuple

from flask import current_app

# Cloudinary import with fallback
try:
	import cloudinary
	import cloudinary.uploader
	CLOUDINARY_AVAILABLE = True
except ImportError:
	CLOUDINARY_AVAILABLE = False


def _supabase_headers():
	key = current_app.config.get("SUPABASE_SERVICE_KEY")
	return {"Authorization": f"Bearer {key}", "apikey": key}

def _public_url(bucket: str, object_path: str) -> str:
	base = current_app.config.get("SUPABASE_URL").rstrip("/")
	return f"{base}/storage/v1/object/public/{bucket}/{object_path}"

def upload_to_bucket(bucket: str, object_path: str, file_bytes: bytes, mimetype: Optional[str] = None) -> Optional[str]:
	base = current_app.config.get("SUPABASE_URL", "").rstrip("/")
	key = current_app.config.get("SUPABASE_SERVICE_KEY", "")
	if not base or not key:
		return None
	url = f"{base}/storage/v1/object/{bucket}/{object_path}"
	headers = _supabase_headers()
	if mimetype:
		headers["Content-Type"] = mimetype
	resp = requests.post(url, headers=headers, data=file_bytes, timeout=30)
	if resp.status_code in (200, 201):
		return _public_url(bucket, object_path)
	# If object exists, try upsert via PUT
	if resp.status_code == 409:
		resp = requests.put(url, headers=headers, data=file_bytes, timeout=30)
		if resp.status_code in (200, 201):
			return _public_url(bucket, object_path)
	current_app.logger.warning("Supabase upload failed %s: %s", resp.status_code, resp.text)
	return None

def generate_user_object_path(user_id: int, filename: str) -> str:
	uid = uuid.uuid4().hex[:12]
	return f"user_{user_id}/{uid}_{filename}"


def _is_production() -> bool:
	"""Check if we're in production environment"""
	return os.getenv("FLASK_ENV") == "production" or os.getenv("ENVIRONMENT") == "production"


def _configure_cloudinary():
	"""Configure Cloudinary if available and in production"""
	if not CLOUDINARY_AVAILABLE or not _is_production():
		return False
	
	cloud_name = current_app.config.get("CLOUDINARY_CLOUD_NAME")
	api_key = current_app.config.get("CLOUDINARY_API_KEY")
	api_secret = current_app.config.get("CLOUDINARY_API_SECRET")
	
	if not all([cloud_name, api_key, api_secret]):
		current_app.logger.warning("Cloudinary credentials not configured")
		return False
	
	cloudinary.config(
		cloud_name=cloud_name,
		api_key=api_key,
		api_secret=api_secret
	)
	return True


def upload_file(file_bytes: bytes, filename: str, mimetype: Optional[str] = None, user_id: int = None) -> Tuple[Optional[str], Optional[str]]:
	"""
	Upload file to appropriate storage (Cloudinary for production, local for development)
	Returns (file_url, file_path) where file_path is None for cloud storage
	"""
	if _is_production() and _configure_cloudinary():
		return _upload_to_cloudinary(file_bytes, filename, mimetype, user_id)
	else:
		return _upload_to_local(file_bytes, filename, mimetype, user_id)


def _upload_to_cloudinary(file_bytes: bytes, filename: str, mimetype: Optional[str] = None, user_id: int = None) -> Tuple[Optional[str], None]:
	"""Upload file to Cloudinary"""
	try:
		# Generate unique public ID
		uid = uuid.uuid4().hex[:12]
		public_id = f"{current_app.config.get('CLOUDINARY_FOLDER', 'life-dashboards')}/user_{user_id or 'unknown'}/{uid}_{filename}"
		
		# Upload to Cloudinary
		result = cloudinary.uploader.upload(
			file_bytes,
			public_id=public_id,
			resource_type="auto",  # Auto-detect file type
			folder=current_app.config.get('CLOUDINARY_FOLDER', 'life-dashboards')
		)
		
		return result.get('secure_url'), None
	except Exception as e:
		current_app.logger.error(f"Cloudinary upload failed: {e}")
		return None, None


def _upload_to_local(file_bytes: bytes, filename: str, mimetype: Optional[str] = None, user_id: int = None) -> Tuple[None, Optional[str]]:
	"""Upload file to local storage"""
	try:
		# Create user-specific directory
		upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
		user_folder = os.path.join(upload_folder, f"user_{user_id or 'unknown'}")
		os.makedirs(user_folder, exist_ok=True)
		
		# Generate unique filename
		uid = uuid.uuid4().hex[:12]
		name, ext = os.path.splitext(filename)
		unique_filename = f"{uid}_{name}{ext}"
		file_path = os.path.join(user_folder, unique_filename)
		
		# Save file
		with open(file_path, 'wb') as f:
			f.write(file_bytes)
		
		return None, file_path
	except Exception as e:
		current_app.logger.error(f"Local upload failed: {e}")
		return None, None


def get_file_url(file_asset) -> Optional[str]:
	"""
	Get the appropriate URL for a file asset
	For cloud storage, returns the cloud URL
	For local storage, returns None (use view_file route instead)
	"""
	if file_asset.filepath and file_asset.filepath.startswith('http'):
		# Already a cloud URL
		return file_asset.filepath
	elif file_asset.filepath and os.path.exists(file_asset.filepath):
		# Local file - return None to use view_file route
		return None
	else:
		# File not found
		return None
