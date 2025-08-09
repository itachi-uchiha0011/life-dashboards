import io
import json
from datetime import date
from flask import jsonify, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from ..extensions import db
from ..models import User, Habit, HabitLog, JournalEntry, Category, Subpage, FileAsset, TodoItem, Reminder
from . import exports_bp


@exports_bp.route("/export.json")
@login_required
def export_json():
    def serialize(model):
        return {c.name: getattr(model, c.name) for c in model.__table__.columns}

    data = {
        "user": serialize(current_user),
        "habits": [serialize(x) for x in Habit.query.filter_by(user_id=current_user.id).all()],
        "habit_logs": [serialize(x) for x in HabitLog.query.filter_by(user_id=current_user.id).all()],
        "journal_entries": [serialize(x) for x in JournalEntry.query.filter_by(user_id=current_user.id).all()],
        "categories": [serialize(x) for x in Category.query.filter_by(user_id=current_user.id).all()],
        "subpages": [serialize(x) for x in Subpage.query.filter_by(user_id=current_user.id).all()],
        "files": [serialize(x) for x in FileAsset.query.filter_by(user_id=current_user.id).all()],
        "todos": [serialize(x) for x in TodoItem.query.filter_by(user_id=current_user.id).all()],
        "reminders": [serialize(x) for x in Reminder.query.filter_by(user_id=current_user.id).all()],
    }
    return jsonify(data)


@exports_bp.route("/import", methods=["POST"]) 
@login_required
def import_json():
    file = request.files.get("file")
    if not file:
        flash("No file.", "danger")
        return redirect(url_for("dashboard.index"))
    try:
        payload = json.load(file)
    except Exception:
        flash("Invalid JSON.", "danger")
        return redirect(url_for("dashboard.index"))

    # Naive import: only journal and habits to avoid conflicts
    for h in payload.get("habits", []):
        if h.get("user_id") == current_user.id:
            exists = Habit.query.filter_by(user_id=current_user.id, name=h.get("name")).first()
            if not exists:
                habit = Habit(
                    user_id=current_user.id,
                    name=h.get("name"),
                    frequency=h.get("frequency", "daily"),
                    custom_days=h.get("custom_days"),
                    category=h.get("category"),
                    color=h.get("color"),
                    icon=h.get("icon"),
                )
                db.session.add(habit)
    for je in payload.get("journal_entries", []):
        if je.get("user_id") == current_user.id:
            d = date.fromisoformat(je.get("entry_date")) if isinstance(je.get("entry_date"), str) else date.today()
            entry = JournalEntry.query.filter_by(user_id=current_user.id, entry_date=d).first()
            if not entry:
                entry = JournalEntry(user_id=current_user.id, entry_date=d, title=je.get("title"), content=je.get("content"))
                db.session.add(entry)
    db.session.commit()
    flash("Import completed (habits, journal).", "success")
    return redirect(url_for("dashboard.index"))


@exports_bp.route("/journal-day.pdf/<string:entry_date>")
@login_required
def export_journal_day_pdf(entry_date: str):
    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=letter)
    textobject = p.beginText(40, 750)
    textobject.setFont("Times-Roman", 14)
    textobject.textLine(f"Journal for {entry_date}")

    entry = JournalEntry.query.filter_by(user_id=current_user.id, entry_date=date.fromisoformat(entry_date)).first()
    content = (entry.title or "") + "\n\n" + (entry.content or "") if entry else "No entry."
    for line in content.splitlines():
        textobject.textLine(line)
    p.drawText(textobject)
    p.showPage()
    p.save()
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name=f"journal_{entry_date}.pdf")