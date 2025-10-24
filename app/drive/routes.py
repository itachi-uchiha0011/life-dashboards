from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from urllib.parse import urlparse, parse_qs
import secrets

from ..services.google_drive import GoogleDriveService
from ..extensions import db
from ..models import GoogleDriveToken, DriveBackup

drive_bp = Blueprint('drive', __name__, url_prefix='/drive')

@drive_bp.route('/connect')
@login_required
def connect():
    """Initiate Google Drive connection"""
    drive_service = GoogleDriveService()
    
    if not drive_service.is_configured:
        flash('Google Drive integration is not configured. Please contact your administrator.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    try:
        auth_url, state = drive_service.get_authorization_url()
        
        # Store state in session for security
        session['google_oauth_state'] = state
        
        return redirect(auth_url)
    except Exception as e:
        flash(f'Failed to initiate Google Drive connection: {str(e)}', 'error')
        return redirect(url_for('dashboard.settings'))

@drive_bp.route('/callback')
@login_required
def callback():
    """Handle Google OAuth callback"""
    # Verify state parameter
    stored_state = session.get('google_oauth_state')
    if not stored_state or request.args.get('state') != stored_state:
        flash('Invalid state parameter. Please try again.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    # Clear state from session
    session.pop('google_oauth_state', None)
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        flash('Authorization failed. Please try again.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    # Handle the callback
    drive_service = GoogleDriveService()
    success = drive_service.handle_callback(
        request.url, 
        request.args.get('state'), 
        current_user.id
    )
    
    if success:
        flash('Google Drive connected successfully!', 'success')
    else:
        flash('Failed to connect Google Drive. Please try again.', 'error')
    
    return redirect(url_for('dashboard.settings'))

@drive_bp.route('/disconnect')
@login_required
def disconnect():
    """Disconnect Google Drive"""
    drive_service = GoogleDriveService()
    success = drive_service.disconnect(current_user.id)
    
    if success:
        flash('Google Drive disconnected successfully.', 'success')
    else:
        flash('Failed to disconnect Google Drive.', 'error')
    
    return redirect(url_for('dashboard.settings'))

@drive_bp.route('/status')
@login_required
def status():
    """Get Google Drive connection status"""
    drive_service = GoogleDriveService()
    is_connected = drive_service.is_connected(current_user.id)
    
    return jsonify({
        'connected': is_connected,
        'has_credentials': GoogleDriveToken.query.filter_by(user_id=current_user.id).first() is not None
    })

@drive_bp.route('/backup-journal/<int:journal_id>')
@login_required
def backup_journal(journal_id):
    """Backup a specific journal entry to Google Drive"""
    from ..models import JournalEntry
    
    journal_entry = JournalEntry.query.filter_by(
        id=journal_id, 
        user_id=current_user.id
    ).first()
    
    if not journal_entry:
        return jsonify({'success': False, 'message': 'Journal entry not found'})
    
    drive_service = GoogleDriveService()
    if not drive_service.is_connected(current_user.id):
        return jsonify({'success': False, 'message': 'Google Drive not connected'})
    
    success = drive_service.backup_journal_entry(current_user.id, journal_entry)
    
    if success:
        return jsonify({'success': True, 'message': 'Journal entry backed up successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to backup journal entry'})

@drive_bp.route('/backup-all-journals')
@login_required
def backup_all_journals():
    """Backup all journal entries to Google Drive"""
    from ..models import JournalEntry
    
    drive_service = GoogleDriveService()
    if not drive_service.is_connected(current_user.id):
        return jsonify({'success': False, 'message': 'Google Drive not connected'})
    
    journal_entries = JournalEntry.query.filter_by(user_id=current_user.id).all()
    success_count = 0
    total_count = len(journal_entries)
    
    for journal_entry in journal_entries:
        if drive_service.backup_journal_entry(current_user.id, journal_entry):
            success_count += 1
    
    return jsonify({
        'success': True, 
        'message': f'Backed up {success_count} out of {total_count} journal entries'
    })

@drive_bp.route('/backups')
@login_required
def list_backups():
    """List all Drive backups for the user"""
    backups = DriveBackup.query.filter_by(user_id=current_user.id).order_by(
        DriveBackup.backup_date.desc()
    ).all()
    
    return render_template('drive/backups.html', backups=backups)

@drive_bp.route('/backup-files')
@login_required
def backup_files():
    """Backup all files to Google Drive"""
    from ..services.backup_service import BackupService
    
    backup_service = BackupService()
    result = backup_service.backup_user_data(current_user.id, ['files'])
    
    return jsonify(result)

@drive_bp.route('/full-export')
@login_required
def full_export():
    """Create full data export"""
    from ..services.backup_service import BackupService
    
    backup_service = BackupService()
    result = backup_service.backup_user_data(current_user.id, ['export'])
    
    return jsonify(result)

@drive_bp.route('/backup-status')
@login_required
def backup_status():
    """Get backup status"""
    from ..services.backup_service import BackupService
    
    backup_service = BackupService()
    status = backup_service.get_backup_status(current_user.id)
    
    return jsonify(status)

@drive_bp.route('/settings')
@login_required
def settings():
    """Google Drive settings page"""
    drive_service = GoogleDriveService()
    
    if not drive_service.is_configured:
        flash('Google Drive integration is not configured. Please contact your administrator.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    is_connected = drive_service.is_connected(current_user.id)
    
    # Get recent backups
    recent_backups = DriveBackup.query.filter_by(user_id=current_user.id).order_by(
        DriveBackup.backup_date.desc()
    ).limit(5).all()
    
    return render_template('drive/settings.html', 
                         is_connected=is_connected, 
                         recent_backups=recent_backups,
                         drive_available=True)

@drive_bp.route('/test-connection')
@login_required
def test_connection():
    """Test Google Drive connection"""
    drive_service = GoogleDriveService()
    
    if not drive_service.is_connected(current_user.id):
        return jsonify({'success': False, 'message': 'Google Drive not connected'})
    
    # Try to create a test folder
    test_folder_id = drive_service.create_folder(
        current_user.id, 
        f"Test Connection {secrets.token_hex(4)}"
    )
    
    if test_folder_id:
        # Clean up test folder
        service = drive_service.get_service(current_user.id)
        if service:
            try:
                service.files().delete(fileId=test_folder_id).execute()
            except:
                pass  # Ignore cleanup errors
        
        return jsonify({'success': True, 'message': 'Google Drive connection working'})
    else:
        return jsonify({'success': False, 'message': 'Failed to connect to Google Drive'})