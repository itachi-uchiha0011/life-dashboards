from datetime import date, timedelta
from flask import jsonify, request
from flask_login import login_required, current_user

from ..extensions import db
from ..models import JournalEntry, TodoItem
from . import api_bp


@api_bp.get("/journal/heatmap")
@login_required
def journal_heatmap():
    # Return counts per day for last 365 days
    start = date.today() - timedelta(days=365)
    entries = (
        JournalEntry.query
        .filter(JournalEntry.user_id == current_user.id, JournalEntry.entry_date >= start)
        .all()
    )
    counts = {}
    for e in entries:
        key = e.entry_date.isoformat()
        counts[key] = counts.get(key, 0) + 1
    data = [{"date": k, "count": v} for k, v in sorted(counts.items())]
    return jsonify(data)


@api_bp.post("/todos")
@login_required
def create_todo():
    payload = request.get_json(force=True)
    item = TodoItem(user_id=current_user.id, label=payload.get("label", ""), kind=payload.get("kind", "todo"))
    db.session.add(item)
    db.session.commit()
    return jsonify({"id": item.id})


@api_bp.post("/todos/<int:item_id>/toggle")
@login_required
def toggle_todo(item_id: int):
    item = TodoItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    item.is_done = not item.is_done
    db.session.commit()
    return jsonify({"ok": True, "is_done": item.is_done})