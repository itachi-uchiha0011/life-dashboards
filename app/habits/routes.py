from datetime import date, datetime
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Habit, HabitLog
from . import habits_bp


@habits_bp.route("/")
@login_required
def list_habits():
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    return render_template("habits/list.html", habits=habits)


@habits_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_habit():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        frequency = request.form.get("frequency", "daily")
        custom_days = request.form.get("custom_days") or None
        category = request.form.get("category") or None
        color = request.form.get("color") or "#0d6efd"
        icon = request.form.get("icon") or None
        sd = request.form.get("start_date") or None
        ed = request.form.get("end_date") or None
        start_date = datetime.strptime(sd, "%Y-%m-%d").date() if sd else None
        end_date = datetime.strptime(ed, "%Y-%m-%d").date() if ed else None
        habit = Habit(
            user_id=current_user.id,
            name=name,
            frequency=frequency,
            custom_days=custom_days,
            category=category,
            color=color,
            icon=icon,
            start_date=start_date,
            end_date=end_date,
        )
        db.session.add(habit)
        db.session.commit()
        flash("Habit created.", "success")
        return redirect(url_for("habits.list_habits"))
    return render_template("habits/create.html")


@habits_bp.route("/<int:habit_id>/edit", methods=["GET", "POST"])
@login_required
def edit_habit(habit_id: int):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        habit.name = request.form.get("name", habit.name)
        habit.frequency = request.form.get("frequency", habit.frequency)
        habit.custom_days = request.form.get("custom_days") or None
        habit.category = request.form.get("category") or None
        habit.color = request.form.get("color") or habit.color
        habit.icon = request.form.get("icon") or None
        sd = request.form.get("start_date") or None
        ed = request.form.get("end_date") or None
        habit.start_date = datetime.strptime(sd, "%Y-%m-%d").date() if sd else None
        habit.end_date = datetime.strptime(ed, "%Y-%m-%d").date() if ed else None
        db.session.commit()
        flash("Habit updated.", "success")
        return redirect(url_for("habits.list_habits"))
    return render_template("habits/edit.html", habit=habit)


@habits_bp.route("/<int:habit_id>/delete", methods=["POST"]) 
@login_required
def delete_habit(habit_id: int):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    db.session.delete(habit)
    db.session.commit()
    flash("Habit deleted.", "info")
    return redirect(url_for("habits.list_habits"))


@habits_bp.route("/<int:habit_id>/toggle_today", methods=["POST"]) 
@login_required
def toggle_today(habit_id: int):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    today = date.today()
    log = HabitLog.query.filter_by(user_id=current_user.id, habit_id=habit.id, log_date=today).first()
    if log:
        db.session.delete(log)
        db.session.commit()
        flash("Unchecked today's habit.", "info")
    else:
        log = HabitLog(user_id=current_user.id, habit_id=habit.id, log_date=today, completed=True)
        db.session.add(log)
        db.session.commit()
        flash("Checked today's habit.", "success")
    return redirect(request.referrer or url_for("dashboard.index"))