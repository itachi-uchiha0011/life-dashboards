from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

from ..extensions import db
from ..models import Category, Subpage, FileAsset
from ..config import Config
from . import categories_bp


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@categories_bp.route("/")
@login_required
def list_categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template("categories/list.html", categories=categories)


@categories_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_category():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name required.", "danger")
            return render_template("categories/create.html")
        cat = Category(user_id=current_user.id, name=name)
        db.session.add(cat)
        db.session.commit()
        flash("Category created.", "success")
        return redirect(url_for("categories.list_categories"))
    return render_template("categories/create.html")


@categories_bp.route("/<int:category_id>")
@login_required
def view_category(category_id: int):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    return render_template("categories/view.html", category=category)


@categories_bp.route("/<int:category_id>/delete", methods=["POST"]) 
@login_required
def delete_category(category_id: int):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted.", "info")
    return redirect(url_for("categories.list_categories"))


@categories_bp.route("/<int:category_id>/subpages/create", methods=["GET", "POST"]) 
@login_required
def create_subpage(category_id: int):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content")
        sp = Subpage(user_id=current_user.id, category_id=category.id, title=title, content=content)
        db.session.add(sp)
        db.session.commit()
        flash("Subpage created.", "success")
        return redirect(url_for("categories.view_subpage", subpage_id=sp.id))
    return render_template("categories/subpages/create.html", category=category)


@categories_bp.route("/subpages/<int:subpage_id>", methods=["GET", "POST"]) 
@login_required
def view_subpage(subpage_id: int):
    sp = Subpage.query.filter_by(id=subpage_id, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        sp.title = request.form.get("title", sp.title)
        sp.content = request.form.get("content")
        db.session.commit()
        flash("Subpage saved.", "success")
        return redirect(url_for("categories.view_subpage", subpage_id=sp.id))
    return render_template("categories/subpages/view.html", subpage=sp)


@categories_bp.route("/subpages/<int:subpage_id>/upload", methods=["POST"]) 
@login_required
def upload_to_subpage(subpage_id: int):
    sp = Subpage.query.filter_by(id=subpage_id, user_id=current_user.id).first_or_404()
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("No file selected.", "danger")
        return redirect(url_for("categories.view_subpage", subpage_id=sp.id))
    if not allowed_file(file.filename):
        flash("File type not allowed.", "danger")
        return redirect(url_for("categories.view_subpage", subpage_id=sp.id))

    user_folder = os.path.join(Config.UPLOAD_FOLDER, f"user_{current_user.id}")
    os.makedirs(user_folder, exist_ok=True)

    filename = secure_filename(file.filename)
    filepath = os.path.join(user_folder, filename)
    file.save(filepath)

    asset = FileAsset(
        user_id=current_user.id,
        subpage_id=sp.id,
        filename=filename,
        filepath=filepath,
        mimetype=file.mimetype,
    )
    db.session.add(asset)
    db.session.commit()
    flash("File uploaded.", "success")
    return redirect(url_for("categories.view_subpage", subpage_id=sp.id))