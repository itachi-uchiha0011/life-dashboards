# Google Drive Integration

This document describes the Google Drive integration added to your Life Dashboard Flask app.

## Features

✅ **User Authentication**: Each user connects their own Google account
✅ **OAuth 2.0 Flow**: Secure authorization without storing passwords
✅ **Automatic Backups**: Journals, files, and data exports to Google Drive
✅ **Organized Storage**: Data is organized in folders by year/month
✅ **Manual Backup Controls**: Users can trigger backups on demand
✅ **Status Monitoring**: Track backup status and connection health

## Setup Instructions

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Drive API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Set application type to "Web application"
6. Add authorized redirect URI: `http://localhost:5000/drive/callback` (or your domain)
7. Download the credentials JSON file

### 2. Environment Variables

Add these environment variables to your `.env` file:

```bash
# Google Drive Integration
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5000/drive/callback
```

### 3. Database Migration

The integration adds two new tables:
- `google_drive_tokens`: Stores OAuth tokens for each user
- `drive_backups`: Tracks backup history and file metadata

Run the migration:
```bash
python3 -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

## How It Works

### 1. User Connection Flow

1. User clicks "Connect Google Drive" in Settings
2. Redirected to Google OAuth consent screen
3. User authorizes the app to access their Drive
4. App receives authorization code and exchanges for tokens
5. Tokens are securely stored in the database

### 2. Backup System

**Journal Backups:**
- Each journal entry is saved as an HTML file
- Organized in folders: `Life Dashboard Backups/Year/Month/`
- File naming: `YYYY-MM-DD - Title.html`

**File Backups:**
- User-uploaded files are backed up to `Life Dashboard Backups/Files/`
- Original file structure and metadata preserved

**Data Exports:**
- Complete JSON export of all user data
- Includes habits, todos, journal entries, daily scores
- Stored as `life_dashboard_export_YYYYMMDD_HHMMSS.json`

### 3. Security & Privacy

- Each user's data is stored in their own Google Drive
- App only requests minimal necessary permissions
- Tokens are encrypted and stored securely
- Users can disconnect at any time

## API Endpoints

### Authentication
- `GET /drive/connect` - Initiate Google OAuth flow
- `GET /drive/callback` - Handle OAuth callback
- `GET /drive/disconnect` - Disconnect Google Drive
- `GET /drive/status` - Check connection status

### Backup Operations
- `POST /drive/backup-journal/<id>` - Backup specific journal entry
- `GET /drive/backup-all-journals` - Backup all journal entries
- `GET /drive/backup-files` - Backup all files
- `GET /drive/full-export` - Create complete data export
- `GET /drive/backups` - View backup history

## UI Components

### Dashboard Integration
- Connection status indicator in main dashboard
- Quick access to settings and backup controls

### Settings Page
- Google Drive connection management
- Manual backup triggers
- Backup status and history
- Connection testing

### Journal Integration
- "Backup to Drive" button on each journal entry
- Real-time backup status feedback

## File Structure

```
app/
├── drive/
│   ├── __init__.py
│   └── routes.py          # Google Drive routes
├── services/
│   ├── __init__.py
│   ├── google_drive.py    # Drive API service
│   └── backup_service.py  # Backup orchestration
├── models.py              # Updated with Drive models
└── templates/
    └── drive/
        ├── settings.html  # Drive settings page
        └── backups.html   # Backup history
```

## Usage Examples

### Connect Google Drive
```python
from app.services.google_drive import GoogleDriveService

drive_service = GoogleDriveService()
auth_url, state = drive_service.get_authorization_url()
# Redirect user to auth_url
```

### Backup Journal Entry
```python
from app.services.google_drive import GoogleDriveService

drive_service = GoogleDriveService()
success = drive_service.backup_journal_entry(user_id, journal_entry)
```

### Check Connection Status
```python
from app.services.google_drive import GoogleDriveService

drive_service = GoogleDriveService()
is_connected = drive_service.is_connected(user_id)
```

## Troubleshooting

### Common Issues

1. **"Google Drive not connected"**
   - User needs to complete OAuth flow
   - Check if tokens are expired and need refresh

2. **"Failed to backup"**
   - Check Google Drive API quotas
   - Verify user has sufficient Drive storage
   - Check network connectivity

3. **"Invalid state parameter"**
   - OAuth state mismatch (security feature)
   - User should retry the connection process

### Debug Mode

Enable debug logging in your Flask app to see detailed Google Drive API responses:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- [ ] Automatic scheduled backups
- [ ] Backup conflict resolution
- [ ] Selective backup options
- [ ] Backup restore functionality
- [ ] Multiple Google account support
- [ ] Backup compression and encryption