from datetime import date
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Habit, HabitLog, TodoItem, JournalEntry
from ..services.google_drive import GoogleDriveService
from . import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():
    today = date.today()
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    today_logs = HabitLog.query.filter_by(user_id=current_user.id, log_date=today).all()
    logs_map = {log.habit_id: log for log in today_logs}

    todos = (
        TodoItem.query.filter_by(user_id=current_user.id, kind="todo")
        .order_by(TodoItem.is_done.asc(), TodoItem.position.asc(), TodoItem.created_at.asc())
        .limit(4)
        .all()
    )
    not_todos = (
        TodoItem.query.filter_by(user_id=current_user.id, kind="not_todo")
        .order_by(TodoItem.is_done.asc(), TodoItem.position.asc(), TodoItem.created_at.asc())
        .limit(4)
        .all()
    )

    # Get today's main journal entry
    today_entry = JournalEntry.query.filter_by(
        user_id=current_user.id, 
        entry_date=today,
        title="Today's Journal"
    ).first()

    # Check Google Drive connection status
    drive_service = GoogleDriveService()
    drive_connected = drive_service.is_configured and drive_service.is_connected(current_user.id)
    drive_available = drive_service.is_configured

    return render_template(
        "dashboard/index.html",
        habits=habits,
        logs_map=logs_map,
        todos=todos,
        not_todos=not_todos,
        today_entry=today_entry,
        today=today,
        drive_connected=drive_connected,
        drive_available=drive_available,
    )


@dashboard_bp.route("/settings")
@login_required
def settings():
    """Settings page with Google Drive integration"""
    drive_service = GoogleDriveService()
    drive_connected = drive_service.is_configured and drive_service.is_connected(current_user.id)
    drive_available = drive_service.is_configured
    
    if not drive_available:
        return render_template("dashboard/settings.html", 
                             drive_connected=drive_connected, 
                             drive_available=drive_available)
    
    return render_template("drive/settings.html", 
                         drive_connected=drive_connected, 
                         drive_available=drive_available)