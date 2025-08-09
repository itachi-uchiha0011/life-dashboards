from datetime import datetime, date
import smtplib
from email.message import EmailMessage
import requests

from flask import current_app
from .extensions import db, scheduler
from .models import Reminder, Habit, HabitLog, User


def send_email(to_address: str, subject: str, body: str) -> None:
    if not to_address:
        return
    server = current_app.config.get("MAIL_SERVER")
    port = current_app.config.get("MAIL_PORT")
    username = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")
    sender = current_app.config.get("MAIL_DEFAULT_SENDER") or username
    if not (server and username and password):
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_address
    msg.set_content(body)
    with smtplib.SMTP(server, port) as smtp:
        if current_app.config.get("MAIL_USE_TLS"):
            smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(msg)


def send_telegram(chat_id: str, text: str) -> None:
    token = current_app.config.get("TELEGRAM_BOT_TOKEN")
    if not (token and chat_id):
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception:
        pass


def schedule_jobs() -> None:
    # Frequent job checks reminders
    if not scheduler.get_job("reminder_tick"):
        scheduler.add_job(check_and_send_reminders, "interval", minutes=1, id="reminder_tick", max_instances=1, replace_existing=True)

    # Daily summary at 21:00 local server time
    if not scheduler.get_job("daily_summary"):
        scheduler.add_job(send_daily_summary, "cron", hour=21, id="daily_summary", replace_existing=True)


def check_and_send_reminders():
    now = datetime.now()
    today = date.today()
    weekday = today.weekday()  # 0=Mon
    reminders = Reminder.query.filter_by(enabled=True).all()
    for r in reminders:
        # Only handle simple daily time + weekdays here
        if r.when_time:
            if r.weekdays:
                allowed = [int(x) for x in r.weekdays.split(",") if x]
                if weekday not in allowed:
                    continue
            if now.hour == r.when_time.hour and now.minute == r.when_time.minute:
                message = "Habit reminder"
                if r.habit_id:
                    habit = Habit.query.get(r.habit_id)
                    message = f"Reminder: {habit.name}"
                user = User.query.get(r.user_id)
                if r.channel == "email":
                    send_email(user.email, "Reminder", message)
                else:
                    send_telegram(current_app.config.get("TELEGRAM_CHAT_ID"), message)


def send_daily_summary():
    today = date.today()
    for user in User.query.all():
        logs = HabitLog.query.filter_by(user_id=user.id, log_date=today, completed=True).count()
        subject = "Your daily summary"
        body = f"You completed {logs} habits today. Keep it up!"
        send_email(user.email, subject, body)