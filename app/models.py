from __future__ import annotations
from datetime import datetime, date
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, Enum

from .extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    timezone = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    habits = db.relationship("Habit", backref="user", lazy=True, cascade="all, delete-orphan")
    habit_logs = db.relationship("HabitLog", backref="user", lazy=True, cascade="all, delete-orphan")
    journal_entries = db.relationship("JournalEntry", backref="user", lazy=True, cascade="all, delete-orphan")
    categories = db.relationship("Category", backref="user", lazy=True, cascade="all, delete-orphan")
    subpages = db.relationship("Subpage", backref="user", lazy=True, cascade="all, delete-orphan")
    files = db.relationship("FileAsset", backref="user", lazy=True, cascade="all, delete-orphan")
    todos = db.relationship("TodoItem", backref="user", lazy=True, cascade="all, delete-orphan")
    daily_scores = db.relationship("DailyScore", backref="user", lazy=True, cascade="all, delete-orphan")
    google_drive_tokens = db.relationship("GoogleDriveToken", backref="user", lazy=True, cascade="all, delete-orphan")
    drive_backups = db.relationship("DriveBackup", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Habit(db.Model):
    __tablename__ = "habits"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    frequency = db.Column(db.String(50), nullable=False, default="daily")  # daily, weekly, custom
    custom_days = db.Column(db.String(20), nullable=True)  # e.g. "1,3,5" for Mon,Wed,Fri (0=Sun)
    category = db.Column(db.String(50), nullable=True)  # Trading, Learning, Fitness, Personal
    color = db.Column(db.String(20), nullable=True, default="#0d6efd")
    icon = db.Column(db.String(50), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    logs = db.relationship("HabitLog", backref="habit", lazy=True, cascade="all, delete-orphan")
    reminders = db.relationship("Reminder", backref="habit", lazy=True, cascade="all, delete-orphan")


class HabitLog(db.Model):
    __tablename__ = "habit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True)
    log_date = db.Column(db.Date, nullable=False, index=True, default=date.today)
    completed = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "habit_id", "log_date", name="uq_habit_log_once_per_day"),)


class JournalEntry(db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_date = db.Column(db.Date, index=True, nullable=False, default=date.today)
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=True)  # rich HTML
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    subpages = db.relationship("Subpage", backref="category", lazy=True, cascade="all, delete-orphan")


class Subpage(db.Model):
    __tablename__ = "subpages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)  # rich HTML (Quill)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    files = db.relationship("FileAsset", backref="subpage", lazy=True, cascade="all, delete-orphan")


class FileAsset(db.Model):
    __tablename__ = "file_assets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subpage_id = db.Column(db.Integer, db.ForeignKey("subpages.id", ondelete="CASCADE"), nullable=True, index=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    mimetype = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class TodoItem(db.Model):
    __tablename__ = "todo_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    label = db.Column(db.String(255), nullable=False)
    kind = db.Column(db.String(20), nullable=False, default="todo")  # todo or not_todo
    is_done = db.Column(db.Boolean, default=False, nullable=False)
    position = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.id", ondelete="CASCADE"), nullable=True, index=True)
    channel = db.Column(db.String(20), nullable=False, default="email")  # email or telegram
    cron = db.Column(db.String(100), nullable=True)  # for advanced schedules
    when_time = db.Column(db.Time, nullable=True)  # simple daily/weekly time
    weekdays = db.Column(db.String(20), nullable=True)  # e.g. "0,1,2" for Sun,Mon,Tue
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class DailyScore(db.Model):
    __tablename__ = "daily_scores"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True, default=date.today)
    do_points = db.Column(db.Integer, default=0, nullable=False)  # 0-4 points
    dont_points = db.Column(db.Integer, default=0, nullable=False)  # 0-4 points
    journal_point = db.Column(db.Integer, default=0, nullable=False)  # 0-1 point
    learning_point = db.Column(db.Integer, default=0, nullable=False)  # 0-1 point
    total_points = db.Column(db.Integer, default=0, nullable=False)  # calculated field
    journal_text = db.Column(db.Text, nullable=True)  # what user learned
    learning_text = db.Column(db.Text, nullable=True)  # mistakes/learnings today
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "date", name="uq_daily_score_once_per_day"),)

    def calculate_total_points(self):
        """Calculate total points from all components"""
        self.total_points = self.do_points + self.dont_points + self.journal_point + self.learning_point
        return self.total_points

    def get_score_color(self):
        """Get color based on total points"""
        if self.total_points >= 7:
            return "green"
        elif self.total_points >= 4:
            return "yellow"
        else:
            return "red"


class GoogleDriveToken(db.Model):
    __tablename__ = "google_drive_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    token_uri = db.Column(db.String(500), nullable=True)
    client_id = db.Column(db.String(500), nullable=True)
    client_secret = db.Column(db.String(500), nullable=True)
    scopes = db.Column(db.Text, nullable=True)  # JSON array of scopes
    expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def is_expired(self) -> bool:
        """Check if the token is expired"""
        if not self.expiry:
            return True
        return datetime.utcnow() >= self.expiry

    def to_credentials_dict(self) -> dict:
        """Convert to google-auth credentials format"""
        return {
            "token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_uri": self.token_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scopes": self.scopes.split(",") if self.scopes else [],
            "expiry": self.expiry.isoformat() if self.expiry else None
        }


class DriveBackup(db.Model):
    __tablename__ = "drive_backups"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    backup_type = db.Column(db.String(50), nullable=False)  # journal, file, export, etc.
    file_id = db.Column(db.String(255), nullable=False)  # Google Drive file ID
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)  # Local file path if applicable
    mime_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    backup_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_synced = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default="active", nullable=False)  # active, deleted, error

    __table_args__ = (db.UniqueConstraint("user_id", "file_id", name="uq_user_drive_file"),)


def get_user_streak(user_id: int, habit_id: int) -> int:
    today = date.today()
    streak = 0
    cur = today
    while True:
        log = (
            HabitLog.query.filter_by(user_id=user_id, habit_id=habit_id, log_date=cur, completed=True)
            .first()
        )
        if log:
            streak += 1
            cur = cur.fromordinal(cur.toordinal() - 1)
        else:
            break
    return streak