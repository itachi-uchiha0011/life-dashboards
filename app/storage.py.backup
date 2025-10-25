import io
import uuid
import requests
from typing import Optional

from flask import current_app


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