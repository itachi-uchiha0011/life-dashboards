from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from ..extensions import db
from ..models import User
from . import auth_bp
from ..storage import upload_to_bucket, generate_user_object_path


def _get_serializer() -> URLSafeTimedSerializer:
    secret = current_app.config.get("SECRET_KEY")
    return URLSafeTimedSerializer(secret_key=secret, salt="password-reset")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        username = (request.form.get("username") or "").strip().lower() or None
        password = request.form.get("password", "")
        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("auth/register.html")
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return render_template("auth/register.html")
        if username and User.query.filter_by(username=username).first():
            flash("Username already taken.", "warning")
            return render_template("auth/register.html")
        user = User(email=email, username=username)
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


@auth_bp.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        # Respond generically to avoid account enumeration
        flash("If that email exists, a reset link has been sent.", "info")
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                s = _get_serializer()
                token = s.dumps({"uid": user.id})
                reset_url = url_for("auth.reset_password", token=token, _external=True)
                # Send email if configured
                try:
                    from ..jobs import send_email
                    send_email(email, "Password reset", f"Click to reset your password: {reset_url}")
                except Exception:
                    current_app.logger.info("Password reset link: %s", reset_url)
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot.html")


@auth_bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    s = _get_serializer()
    try:
        data = s.loads(token, max_age=60*60*24)  # 24h
        user = db.session.get(User, int(data.get("uid")))
        if not user:
            raise BadSignature("user not found")
    except (BadSignature, SignatureExpired):
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        pwd = request.form.get("password") or ""
        if len(pwd) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("auth/reset.html")
        user.set_password(pwd)
        db.session.commit()
        flash("Password updated. You can now log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset.html")


@auth_bp.route("/change-email", methods=["GET", "POST"])
@login_required
def change_email():
    if request.method == "POST":
        new_email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if not current_user.check_password(password):
            flash("Incorrect password.", "danger")
            return render_template("auth/change_email.html")
        if not new_email:
            flash("Email is required.", "danger")
            return render_template("auth/change_email.html")
        if User.query.filter(User.email == new_email, User.id != current_user.id).first():
            flash("That email is already in use.", "warning")
            return render_template("auth/change_email.html")
        current_user.email = new_email
        db.session.commit()
        flash("Email updated.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("auth/change_email.html")


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip().lower() or None
        timezone = (request.form.get("timezone") or "").strip() or None
        if username and User.query.filter(User.username == username, User.id != current_user.id).first():
            flash("Username already taken.", "warning")
            return render_template("auth/profile.html")
        # Avatar upload
        avatar_file = request.files.get("avatar")
        if avatar_file and avatar_file.filename:
            data = avatar_file.read()
            path = generate_user_object_path(current_user.id, avatar_file.filename)
            url = upload_to_bucket(current_app.config.get("SUPABASE_AVATARS_BUCKET", "avatars"), path, data, avatar_file.mimetype)
            if url:
                current_user.avatar_url = url
            else:
                flash("Avatar upload failed.", "warning")
        current_user.username = username
        current_user.timezone = timezone
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html")


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_pwd = request.form.get("current_password") or ""
        new_pwd = request.form.get("new_password") or ""
        if not current_user.check_password(current_pwd):
            flash("Current password is incorrect.", "danger")
            return render_template("auth/change_password.html")
        if len(new_pwd) < 6:
            flash("New password must be at least 6 characters.", "danger")
            return render_template("auth/change_password.html")
        current_user.set_password(new_pwd)
        db.session.commit()
        flash("Password changed.", "success")
        return redirect(url_for("auth.profile"))
    return render_template("auth/change_password.html")