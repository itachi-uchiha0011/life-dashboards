import os
from flask import render_template, send_file, abort
from flask_login import login_required, current_user

from ..models import FileAsset
from . import files_bp


@files_bp.route("/")
@login_required
def list_files():
    files = FileAsset.query.filter_by(user_id=current_user.id).order_by(FileAsset.created_at.desc()).all()
    return render_template("files/list.html", files=files)


@files_bp.route("/download/<int:file_id>")
@login_required
def download_file(file_id: int):
    fa = FileAsset.query.filter_by(id=file_id, user_id=current_user.id).first_or_404()
    if not os.path.exists(fa.filepath):
        abort(404)
    return send_file(fa.filepath, as_attachment=True, download_name=fa.filename)