from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import db
from ..models import User
from . import auth_bp


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("auth/register.html")
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return render_template("auth/register.html")
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for("dashboard.index"))
        flash("Invalid credentials.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))