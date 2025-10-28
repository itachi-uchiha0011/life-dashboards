from datetime import date
from flask import render_template
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Habit, HabitLog, TodoItem, JournalEntry
from . import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():
    today = date.today()
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    today_logs = HabitLog.query.filter_by(user_id=current_user.id, log_date=today).all()
    logs_map = {log.habit_id: log for log in today_logs}

    # Get all todos for expand/collapse functionality
    all_todos = (
        TodoItem.query.filter_by(user_id=current_user.id, kind="todo")
        .order_by(TodoItem.is_done.asc(), TodoItem.position.asc(), TodoItem.created_at.asc())
        .all()
    )
    all_not_todos = (
        TodoItem.query.filter_by(user_id=current_user.id, kind="not_todo")
        .order_by(TodoItem.is_done.asc(), TodoItem.position.asc(), TodoItem.created_at.asc())
        .all()
    )
    
    # Show first 4 by default
    todos = all_todos[:4]
    not_todos = all_not_todos[:4]

    today_entry = JournalEntry.query.filter_by(user_id=current_user.id, entry_date=today).first()

    return render_template(
        "dashboard/index.html",
        habits=habits,
        logs_map=logs_map,
        todos=todos,
        not_todos=not_todos,
        all_todos=all_todos,
        all_not_todos=all_not_todos,
        today_entry=today_entry,
        today=today,
    )