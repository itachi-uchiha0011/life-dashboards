from datetime import date, datetime, timedelta
from calendar import monthrange
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from ..extensions import db
from ..models import DailyScore, UserTask
from ..forms import DailyTaskForm, UserTaskForm
from . import tasks_bp


@tasks_bp.route('/')
@login_required
def daily_tasks():
    """Show daily task checklist form"""
    today = date.today()
    
    # Get today's score if it exists
    today_score = DailyScore.query.filter_by(
        user_id=current_user.id, 
        date=today
    ).first()
    
    # Get user's active tasks
    do_tasks = UserTask.query.filter_by(
        user_id=current_user.id, 
        task_type='do', 
        is_active=True
    ).order_by(UserTask.position.asc()).all()
    
    dont_tasks = UserTask.query.filter_by(
        user_id=current_user.id, 
        task_type='dont', 
        is_active=True
    ).order_by(UserTask.position.asc()).all()
    
    form = DailyTaskForm()
    
    # Pre-populate form if today's score exists
    if today_score:
        form.journal_point.data = today_score.journal_point == 1
        form.learning_point.data = today_score.learning_point == 1
        form.journal_text.data = today_score.journal_text
        form.learning_text.data = today_score.learning_text
    
    return render_template('tasks/daily_tasks.html', 
                         form=form, 
                         today_score=today_score, 
                         today=today,
                         do_tasks=do_tasks,
                         dont_tasks=dont_tasks)


@tasks_bp.route('/submit', methods=['POST'])
@login_required
def submit_daily_tasks():
    """Submit daily task form"""
    form = DailyTaskForm()
    today = date.today()
    
    if form.validate_on_submit():
        # Calculate points from submitted checkboxes
        do_points = 0
        dont_points = 0
        
        # Count checked do tasks
        for key, value in request.form.items():
            if key.startswith('do_task_') and value == 'on':
                do_points += 1
            elif key.startswith('dont_task_') and value == 'on':
                dont_points += 1
        
        journal_point = form.calculate_journal_point()
        learning_point = form.calculate_learning_point()
        
        # Get or create today's score
        today_score = DailyScore.query.filter_by(
            user_id=current_user.id, 
            date=today
        ).first()
        
        if not today_score:
            today_score = DailyScore(
                user_id=current_user.id,
                date=today
            )
            db.session.add(today_score)
        
        # Update score data
        today_score.do_points = do_points
        today_score.dont_points = dont_points
        today_score.journal_point = journal_point
        today_score.learning_point = learning_point
        today_score.journal_text = form.journal_text.data
        today_score.learning_text = form.learning_text.data
        today_score.calculate_total_points()
        today_score.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Daily tasks saved successfully!', 'success')
        return redirect(url_for('tasks.daily_tasks'))
    
    # If form validation fails, show errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('tasks.daily_tasks'))


@tasks_bp.route('/calendar')
@login_required
def calendar():
    """Show monthly calendar view"""
    # Get current month/year from query params or use current date
    year = request.args.get('year', type=int) or date.today().year
    month = request.args.get('month', type=int) or date.today().month
    
    # Validate month/year
    if month < 1 or month > 12:
        month = date.today().month
    if year < 2020 or year > 2030:
        year = date.today().year
    
    # Get first day of month and number of days
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    
    # Get all scores for the month
    scores = DailyScore.query.filter(
        DailyScore.user_id == current_user.id,
        DailyScore.date >= first_day,
        DailyScore.date <= last_day
    ).all()
    
    # Create a dictionary for quick lookup
    scores_dict = {score.date: score for score in scores}
    
    # Calculate calendar grid
    calendar_data = []
    
    # Get the first Monday of the week containing the first day
    start_date = first_day - timedelta(days=first_day.weekday())
    
    # Generate 6 weeks (42 days) to fill the calendar grid
    for week in range(6):
        week_data = []
        for day in range(7):
            current_date = start_date + timedelta(days=week * 7 + day)
            score = scores_dict.get(current_date)
            
            week_data.append({
                'date': current_date,
                'score': score,
                'is_current_month': current_date.month == month,
                'is_today': current_date == date.today()
            })
        calendar_data.append(week_data)
    
    # Calculate navigation dates
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    return render_template(
        'tasks/calendar.html',
        calendar_data=calendar_data,
        current_month=month,
        current_year=year,
        month_name=first_day.strftime('%B'),
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year
    )


@tasks_bp.route('/day-details/<int:year>/<int:month>/<int:day>')
@login_required
def day_details(year, month, day):
    """Get details for a specific day (for tooltips/modals)"""
    try:
        target_date = date(year, month, day)
        score = DailyScore.query.filter_by(
            user_id=current_user.id,
            date=target_date
        ).first()
        
        if score:
            return jsonify({
                'date': target_date.isoformat(),
                'do_points': score.do_points,
                'dont_points': score.dont_points,
                'journal_point': score.journal_point,
                'learning_point': score.learning_point,
                'total_points': score.total_points,
                'journal_text': score.journal_text,
                'learning_text': score.learning_text,
                'color': score.get_score_color()
            })
        else:
            return jsonify({
                'date': target_date.isoformat(),
                'do_points': 0,
                'dont_points': 0,
                'journal_point': 0,
                'learning_point': 0,
                'total_points': 0,
                'journal_text': '',
                'learning_text': '',
                'color': 'gray'
            })
    except ValueError:
        return jsonify({'error': 'Invalid date'}), 400


@tasks_bp.route('/manage-tasks')
@login_required
def manage_tasks():
    """Manage user tasks"""
    do_tasks = UserTask.query.filter_by(
        user_id=current_user.id, 
        task_type='do', 
        is_active=True
    ).order_by(UserTask.position.asc()).all()
    
    dont_tasks = UserTask.query.filter_by(
        user_id=current_user.id, 
        task_type='dont', 
        is_active=True
    ).order_by(UserTask.position.asc()).all()
    
    form = UserTaskForm()
    
    return render_template('tasks/manage_tasks.html', 
                         form=form,
                         do_tasks=do_tasks,
                         dont_tasks=dont_tasks)


@tasks_bp.route('/add-task', methods=['POST'])
@login_required
def add_task():
    """Add a new user task"""
    form = UserTaskForm()
    
    if form.validate_on_submit():
        # Get the next position for this task type
        max_position = db.session.query(db.func.max(UserTask.position)).filter_by(
            user_id=current_user.id,
            task_type=form.task_type.data
        ).scalar() or 0
        
        task = UserTask(
            user_id=current_user.id,
            task_type=form.task_type.data,
            task_text=form.task_text.data,
            position=max_position + 1
        )
        
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('tasks.manage_tasks'))


@tasks_bp.route('/delete-task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a user task"""
    task = UserTask.query.filter_by(
        id=task_id,
        user_id=current_user.id
    ).first()
    
    if task:
        task.is_active = False
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    else:
        flash('Task not found!', 'error')
    
    return redirect(url_for('tasks.manage_tasks'))


@tasks_bp.route('/reorder-tasks', methods=['POST'])
@login_required
def reorder_tasks():
    """Reorder user tasks"""
    data = request.get_json()
    task_type = data.get('task_type')
    task_ids = data.get('task_ids', [])
    
    for i, task_id in enumerate(task_ids):
        task = UserTask.query.filter_by(
            id=task_id,
            user_id=current_user.id,
            task_type=task_type
        ).first()
        if task:
            task.position = i + 1
    
    db.session.commit()
    return jsonify({'success': True})