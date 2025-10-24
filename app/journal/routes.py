from datetime import date, datetime
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from ..extensions import db
from ..models import JournalEntry
from ..services.google_drive import GoogleDriveService
from . import journal_bp


@journal_bp.route("/")
@login_required
def journal_index():
	page = max(int(request.args.get("page", 1)), 1)
	per_page = 100
	q = (JournalEntry.query
		.filter_by(user_id=current_user.id)
		.order_by(JournalEntry.entry_date.desc()))
	entries = q.offset((page-1)*per_page).limit(per_page).all()
	today = date.today()
	return render_template("journal/index.html", entries=entries, today=today, page=page)


@journal_bp.route("/day/<string:entry_date>", methods=["GET", "POST"])
@login_required
def journal_day(entry_date: str):
	try:
		d = datetime.strptime(entry_date, "%Y-%m-%d").date()
	except ValueError:
		flash("Invalid date.", "danger")
		return redirect(url_for("journal.journal_index"))
	entry = JournalEntry.query.filter_by(user_id=current_user.id, entry_date=d).first()
	if request.method == "POST":
		title = request.form.get("title")
		content = request.form.get("content")
		if entry:
			entry.title = title
			entry.content = content
		else:
			entry = JournalEntry(user_id=current_user.id, entry_date=d, title=title, content=content)
			db.session.add(entry)
		db.session.commit()
		flash("Entry saved.", "success")
		return redirect(url_for("journal.journal_day", entry_date=d.isoformat()))
	if not entry:
		entry = JournalEntry(user_id=current_user.id, entry_date=d, title="", content="")
	return render_template("journal/day.html", entry=entry)


@journal_bp.route("/backup/<int:entry_id>", methods=["POST"])
@login_required
def backup_entry(entry_id: int):
	"""Backup a journal entry to Google Drive"""
	entry = JournalEntry.query.filter_by(id=entry_id, user_id=current_user.id).first()
	if not entry:
		return jsonify({"success": False, "message": "Journal entry not found"})
	
	drive_service = GoogleDriveService()
	if not drive_service.is_connected(current_user.id):
		return jsonify({"success": False, "message": "Google Drive not connected"})
	
	success = drive_service.backup_journal_entry(current_user.id, entry)
	
	if success:
		return jsonify({"success": True, "message": "Journal entry backed up successfully"})
	else:
		return jsonify({"success": False, "message": "Failed to backup journal entry"})