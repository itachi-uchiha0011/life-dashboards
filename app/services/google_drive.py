import os
import json
import io
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload

from ..extensions import db
from ..models import GoogleDriveToken, DriveBackup, User
from ..config import Config


class GoogleDriveService:
    """Service for handling Google Drive operations"""
    
    def __init__(self):
        self.client_id = Config.GOOGLE_CLIENT_ID
        self.client_secret = Config.GOOGLE_CLIENT_SECRET
        self.redirect_uri = Config.GOOGLE_REDIRECT_URI
        self.scopes = Config.GOOGLE_DRIVE_SCOPES
        self.is_configured = bool(self.client_id and self.client_secret)
    
    def get_authorization_url(self) -> str:
        """Get Google OAuth authorization URL"""
        if not self.is_configured:
            raise ValueError("Google Drive is not configured. Missing client credentials.")
            
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url, state
    
    def handle_callback(self, authorization_response: str, state: str, user_id: int) -> bool:
        """Handle OAuth callback and store credentials"""
        if not self.is_configured:
            print("Error: Google Drive is not configured. Missing client credentials.")
            return False
            
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials
            
            # Store or update token in database
            token_record = GoogleDriveToken.query.filter_by(user_id=user_id).first()
            if not token_record:
                token_record = GoogleDriveToken(user_id=user_id)
            
            token_record.access_token = credentials.token
            token_record.refresh_token = credentials.refresh_token
            token_record.token_uri = credentials.token_uri
            token_record.client_id = self.client_id
            token_record.client_secret = self.client_secret
            token_record.scopes = ",".join(credentials.scopes) if credentials.scopes else ""
            token_record.expiry = credentials.expiry
            
            db.session.add(token_record)
            db.session.commit()
            
            return True
        except Exception as e:
            print(f"Error handling Google Drive callback: {e}")
            return False
    
    def get_credentials(self, user_id: int) -> Optional[Credentials]:
        """Get valid credentials for user"""
        token_record = GoogleDriveToken.query.filter_by(user_id=user_id).first()
        if not token_record:
            return None
        
        credentials = Credentials.from_authorized_user_info(
            token_record.to_credentials_dict(),
            scopes=self.scopes
        )
        
        # Refresh token if expired
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                # Update stored token
                token_record.access_token = credentials.token
                token_record.expiry = credentials.expiry
                db.session.commit()
            except Exception as e:
                print(f"Error refreshing token: {e}")
                return None
        
        return credentials
    
    def get_service(self, user_id: int):
        """Get Google Drive service instance"""
        credentials = self.get_credentials(user_id)
        if not credentials:
            return None
        
        try:
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            print(f"Error building Drive service: {e}")
            return None
    
    def create_folder(self, user_id: int, folder_name: str, parent_folder_id: str = None) -> Optional[str]:
        """Create a folder in Google Drive"""
        service = self.get_service(user_id)
        if not service:
            return None
        
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            file = service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            return file.get('id')
        except HttpError as e:
            print(f"Error creating folder: {e}")
            return None
    
    def upload_file(self, user_id: int, file_path: str, file_name: str, 
                   mime_type: str = None, parent_folder_id: str = None) -> Optional[str]:
        """Upload a file to Google Drive"""
        service = self.get_service(user_id)
        if not service:
            return None
        
        try:
            file_metadata = {
                'name': file_name
            }
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
        except HttpError as e:
            print(f"Error uploading file: {e}")
            return None
    
    def upload_content(self, user_id: int, content: str, file_name: str, 
                      mime_type: str = 'text/plain', parent_folder_id: str = None) -> Optional[str]:
        """Upload content as a file to Google Drive"""
        service = self.get_service(user_id)
        if not service:
            return None
        
        try:
            file_metadata = {
                'name': file_name
            }
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode('utf-8')),
                mimetype=mime_type
            )
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
        except HttpError as e:
            print(f"Error uploading content: {e}")
            return None
    
    def get_or_create_app_folder(self, user_id: int) -> Optional[str]:
        """Get or create the main app folder for the user"""
        service = self.get_service(user_id)
        if not service:
            return None
        
        try:
            # Search for existing folder
            results = service.files().list(
                q="name='Life Dashboard Backups' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            if files:
                return files[0]['id']
            
            # Create folder if it doesn't exist
            return self.create_folder(user_id, "Life Dashboard Backups")
            
        except HttpError as e:
            print(f"Error getting/creating app folder: {e}")
            return None
    
    def backup_journal_entry(self, user_id: int, journal_entry) -> bool:
        """Backup a journal entry to Google Drive"""
        app_folder_id = self.get_or_create_app_folder(user_id)
        if not app_folder_id:
            return False
        
        # Create year folder
        year = journal_entry.entry_date.year
        year_folder_id = self._get_or_create_year_folder(user_id, year, app_folder_id)
        if not year_folder_id:
            return False
        
        # Create month folder
        month = journal_entry.entry_date.strftime('%B')
        month_folder_id = self._get_or_create_month_folder(user_id, month, year_folder_id)
        if not month_folder_id:
            return False
        
        # Create file name
        file_name = f"{journal_entry.entry_date.strftime('%Y-%m-%d')} - {journal_entry.title or 'Journal Entry'}.html"
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{journal_entry.title or 'Journal Entry'}</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>{journal_entry.title or 'Journal Entry'}</h1>
            <p><strong>Date:</strong> {journal_entry.entry_date.strftime('%B %d, %Y')}</p>
            <div>{journal_entry.content or ''}</div>
        </body>
        </html>
        """
        
        # Upload to Drive
        file_id = self.upload_content(
            user_id, 
            html_content, 
            file_name, 
            'text/html', 
            month_folder_id
        )
        
        if file_id:
            # Record backup
            backup = DriveBackup(
                user_id=user_id,
                backup_type='journal',
                file_id=file_id,
                file_name=file_name,
                mime_type='text/html',
                file_size=len(html_content.encode('utf-8'))
            )
            db.session.add(backup)
            db.session.commit()
            return True
        
        return False
    
    def _get_or_create_year_folder(self, user_id: int, year: int, parent_id: str) -> Optional[str]:
        """Get or create year folder"""
        service = self.get_service(user_id)
        if not service:
            return None
        
        try:
            results = service.files().list(
                q=f"name='{year}' and mimeType='application/vnd.google-apps.folder' and parents in '{parent_id}' and trashed=false",
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            if files:
                return files[0]['id']
            
            return self.create_folder(user_id, str(year), parent_id)
            
        except HttpError as e:
            print(f"Error getting/creating year folder: {e}")
            return None
    
    def _get_or_create_month_folder(self, user_id: int, month: str, parent_id: str) -> Optional[str]:
        """Get or create month folder"""
        service = self.get_service(user_id)
        if not service:
            return None
        
        try:
            results = service.files().list(
                q=f"name='{month}' and mimeType='application/vnd.google-apps.folder' and parents in '{parent_id}' and trashed=false",
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            if files:
                return files[0]['id']
            
            return self.create_folder(user_id, month, parent_id)
            
        except HttpError as e:
            print(f"Error getting/creating month folder: {e}")
            return None
    
    def is_connected(self, user_id: int) -> bool:
        """Check if user has Google Drive connected"""
        token_record = GoogleDriveToken.query.filter_by(user_id=user_id).first()
        return token_record is not None and not token_record.is_expired()
    
    def disconnect(self, user_id: int) -> bool:
        """Disconnect Google Drive for user"""
        try:
            GoogleDriveToken.query.filter_by(user_id=user_id).delete()
            DriveBackup.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error disconnecting Google Drive: {e}")
            return False