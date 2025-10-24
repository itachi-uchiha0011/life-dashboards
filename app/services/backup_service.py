from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import os

from ..extensions import db
from ..models import User, JournalEntry, FileAsset, DriveBackup
from .google_drive import GoogleDriveService


class BackupService:
    """Service for handling automatic backups to Google Drive"""
    
    def __init__(self):
        self.drive_service = GoogleDriveService()
    
    def backup_user_data(self, user_id: int, backup_types: List[str] = None) -> Dict[str, Any]:
        """Backup user data to Google Drive"""
        if not self.drive_service.is_connected(user_id):
            return {
                'success': False,
                'message': 'Google Drive not connected',
                'backups': {}
            }
        
        if backup_types is None:
            backup_types = ['journals', 'files', 'export']
        
        results = {}
        
        if 'journals' in backup_types:
            results['journals'] = self._backup_journals(user_id)
        
        if 'files' in backup_types:
            results['files'] = self._backup_files(user_id)
        
        if 'export' in backup_types:
            results['export'] = self._create_full_export(user_id)
        
        return {
            'success': True,
            'message': 'Backup completed',
            'backups': results
        }
    
    def _backup_journals(self, user_id: int) -> Dict[str, Any]:
        """Backup all journal entries"""
        journal_entries = JournalEntry.query.filter_by(user_id=user_id).all()
        success_count = 0
        total_count = len(journal_entries)
        
        for journal_entry in journal_entries:
            # Check if already backed up recently
            existing_backup = DriveBackup.query.filter_by(
                user_id=user_id,
                backup_type='journal',
                file_name=f"{journal_entry.entry_date.strftime('%Y-%m-%d')} - {journal_entry.title or 'Journal Entry'}.html"
            ).first()
            
            if existing_backup and existing_backup.last_synced > journal_entry.updated_at:
                success_count += 1
                continue
            
            if self.drive_service.backup_journal_entry(user_id, journal_entry):
                success_count += 1
        
        return {
            'type': 'journals',
            'success_count': success_count,
            'total_count': total_count,
            'message': f'Backed up {success_count} out of {total_count} journal entries'
        }
    
    def _backup_files(self, user_id: int) -> Dict[str, Any]:
        """Backup file assets"""
        file_assets = FileAsset.query.filter_by(user_id=user_id).all()
        success_count = 0
        total_count = len(file_assets)
        
        app_folder_id = self.drive_service.get_or_create_app_folder(user_id)
        if not app_folder_id:
            return {
                'type': 'files',
                'success_count': 0,
                'total_count': total_count,
                'message': 'Failed to create app folder'
            }
        
        # Create files folder
        files_folder_id = self._get_or_create_files_folder(user_id, app_folder_id)
        if not files_folder_id:
            return {
                'type': 'files',
                'success_count': 0,
                'total_count': total_count,
                'message': 'Failed to create files folder'
            }
        
        for file_asset in file_assets:
            if not os.path.exists(file_asset.filepath):
                continue
            
            # Check if already backed up
            existing_backup = DriveBackup.query.filter_by(
                user_id=user_id,
                backup_type='file',
                file_name=file_asset.filename
            ).first()
            
            if existing_backup:
                success_count += 1
                continue
            
            # Upload file
            file_id = self.drive_service.upload_file(
                user_id,
                file_asset.filepath,
                file_asset.filename,
                file_asset.mimetype,
                files_folder_id
            )
            
            if file_id:
                # Record backup
                backup = DriveBackup(
                    user_id=user_id,
                    backup_type='file',
                    file_id=file_id,
                    file_name=file_asset.filename,
                    file_path=file_asset.filepath,
                    mime_type=file_asset.mimetype,
                    file_size=os.path.getsize(file_asset.filepath) if os.path.exists(file_asset.filepath) else 0
                )
                db.session.add(backup)
                success_count += 1
        
        db.session.commit()
        
        return {
            'type': 'files',
            'success_count': success_count,
            'total_count': total_count,
            'message': f'Backed up {success_count} out of {total_count} files'
        }
    
    def _create_full_export(self, user_id: int) -> Dict[str, Any]:
        """Create a full data export"""
        user = User.query.get(user_id)
        if not user:
            return {
                'type': 'export',
                'success': False,
                'message': 'User not found'
            }
        
        # Create export data
        export_data = {
            'user': {
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat(),
                'timezone': user.timezone
            },
            'journal_entries': [],
            'habits': [],
            'todos': [],
            'daily_scores': [],
            'export_date': datetime.utcnow().isoformat()
        }
        
        # Export journal entries
        for journal in user.journal_entries:
            export_data['journal_entries'].append({
                'entry_date': journal.entry_date.isoformat(),
                'title': journal.title,
                'content': journal.content,
                'created_at': journal.created_at.isoformat(),
                'updated_at': journal.updated_at.isoformat()
            })
        
        # Export habits
        for habit in user.habits:
            export_data['habits'].append({
                'name': habit.name,
                'frequency': habit.frequency,
                'category': habit.category,
                'color': habit.color,
                'icon': habit.icon,
                'start_date': habit.start_date.isoformat() if habit.start_date else None,
                'end_date': habit.end_date.isoformat() if habit.end_date else None,
                'created_at': habit.created_at.isoformat()
            })
        
        # Export todos
        for todo in user.todos:
            export_data['todos'].append({
                'label': todo.label,
                'kind': todo.kind,
                'is_done': todo.is_done,
                'position': todo.position,
                'created_at': todo.created_at.isoformat()
            })
        
        # Export daily scores
        for score in user.daily_scores:
            export_data['daily_scores'].append({
                'date': score.date.isoformat(),
                'do_points': score.do_points,
                'dont_points': score.dont_points,
                'journal_point': score.journal_point,
                'learning_point': score.learning_point,
                'total_points': score.total_points,
                'journal_text': score.journal_text,
                'learning_text': score.learning_text,
                'created_at': score.created_at.isoformat()
            })
        
        # Create JSON file
        json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
        file_name = f"life_dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Upload to Drive
        file_id = self.drive_service.upload_content(
            user_id,
            json_content,
            file_name,
            'application/json'
        )
        
        if file_id:
            # Record backup
            backup = DriveBackup(
                user_id=user_id,
                backup_type='export',
                file_id=file_id,
                file_name=file_name,
                mime_type='application/json',
                file_size=len(json_content.encode('utf-8'))
            )
            db.session.add(backup)
            db.session.commit()
            
            return {
                'type': 'export',
                'success': True,
                'message': f'Created full export: {file_name}',
                'file_id': file_id
            }
        else:
            return {
                'type': 'export',
                'success': False,
                'message': 'Failed to upload export to Google Drive'
            }
    
    def _get_or_create_files_folder(self, user_id: int, parent_folder_id: str) -> str:
        """Get or create files folder"""
        service = self.drive_service.get_service(user_id)
        if not service:
            return None
        
        try:
            results = service.files().list(
                q="name='Files' and mimeType='application/vnd.google-apps.folder' and parents in '{parent_folder_id}' and trashed=false".format(
                    parent_folder_id=parent_folder_id
                ),
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            if files:
                return files[0]['id']
            
            return self.drive_service.create_folder(user_id, "Files", parent_folder_id)
            
        except Exception as e:
            print(f"Error getting/creating files folder: {e}")
            return None
    
    def get_backup_status(self, user_id: int) -> Dict[str, Any]:
        """Get backup status for user"""
        if not self.drive_service.is_connected(user_id):
            return {
                'connected': False,
                'last_backup': None,
                'total_backups': 0,
                'backup_types': {}
            }
        
        # Get last backup date
        last_backup = DriveBackup.query.filter_by(
            user_id=user_id,
            status='active'
        ).order_by(DriveBackup.backup_date.desc()).first()
        
        # Count backups by type
        backup_counts = db.session.query(
            DriveBackup.backup_type,
            db.func.count(DriveBackup.id)
        ).filter_by(
            user_id=user_id,
            status='active'
        ).group_by(DriveBackup.backup_type).all()
        
        backup_types = {backup_type: count for backup_type, count in backup_counts}
        
        return {
            'connected': True,
            'last_backup': last_backup.backup_date.isoformat() if last_backup else None,
            'total_backups': sum(backup_types.values()),
            'backup_types': backup_types
        }