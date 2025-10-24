from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from .models import User, Category, Subpage

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message='Password must be at least 6 characters')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    
    def validate_username(self, username):
        """Check if username is already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please choose a different one.')

class CategoryForm(FlaskForm):
    """Category creation/editing form"""
    title = StringField('Category Title', validators=[
        DataRequired(), 
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    description = TextAreaField('Description', validators=[
        Optional(), 
        Length(max=1000, message='Description cannot exceed 1000 characters')
    ])
    icon = StringField('Icon', validators=[Optional(), Length(max=50)])
    color = StringField('Color', validators=[Optional(), Length(max=7)], default='#6366f1')

class PageForm(FlaskForm):
    """Page creation/editing form"""
    title = StringField('Page Title', validators=[
        DataRequired(), 
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    icon = StringField('Icon', validators=[Optional(), Length(max=50)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    parent_id = SelectField('Parent Page', coerce=int, validators=[Optional()])
    template_type = SelectField('Template Type', choices=[
        ('', 'None'),
        ('calendar', 'Calendar'),
        ('habit_tracker', 'Habit Tracker'),
        ('kanban', 'Kanban Board'),
        ('notes', 'Notes')
    ], validators=[Optional()])

class ContentBlockForm(FlaskForm):
    """Content block form for AJAX updates"""
    block_id = HiddenField('Block ID')
    block_type = SelectField('Block Type', choices=[
        ('text', 'Text'),
        ('heading1', 'Heading 1'),
        ('heading2', 'Heading 2'),
        ('heading3', 'Heading 3'),
        ('todo', 'Todo'),
        ('bullet', 'Bullet Point'),
        ('quote', 'Quote'),
        ('code', 'Code Block'),
        ('divider', 'Divider'),
        ('image', 'Image'),
        ('file', 'File')
    ], validators=[DataRequired()])
    content = TextAreaField('Content', validators=[Optional()])
    order = HiddenField('Order', default=0)

class FileUploadForm(FlaskForm):
    """File upload form"""
    file = FileField('Upload File', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt', 'md'], 
                   'File type not allowed')
    ])
    page_id = HiddenField('Page ID', validators=[DataRequired()])

class SearchForm(FlaskForm):
    """Search form"""
    query = StringField('Search', validators=[
        DataRequired(), 
        Length(min=1, max=100, message='Search query must be between 1 and 100 characters')
    ])

class QuickAddForm(FlaskForm):
    """Quick add page form"""
    title = StringField('Page Title', validators=[DataRequired(), Length(min=1, max=200)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])

class DailyTaskForm(FlaskForm):
    """Daily task tracking form"""
    # Do's points (4 items, 1 point each)
    do_1 = BooleanField('Do Task 1')
    do_2 = BooleanField('Do Task 2')
    do_3 = BooleanField('Do Task 3')
    do_4 = BooleanField('Do Task 4')
    
    # Don'ts points (4 items, 1 point each)
    dont_1 = BooleanField('Don\'t Task 1')
    dont_2 = BooleanField('Don\'t Task 2')
    dont_3 = BooleanField('Don\'t Task 3')
    dont_4 = BooleanField('Don\'t Task 4')
    
    # Journal and Learning points (1 point each)
    journal_point = BooleanField('Journal Entry')
    learning_point = BooleanField('Learning/Mistake Entry')
    
    # Text areas for content
    journal_text = TextAreaField('What I learned today', validators=[Optional()], 
                                render_kw={"placeholder": "Write about what you learned or accomplished today..."})
    learning_text = TextAreaField('Mistakes and learnings', validators=[Optional()], 
                                 render_kw={"placeholder": "Write about mistakes made and lessons learned today..."})
    
    def calculate_do_points(self):
        """Calculate total do points"""
        return sum([1 for field in [self.do_1, self.do_2, self.do_3, self.do_4] if field.data])
    
    def calculate_dont_points(self):
        """Calculate total dont points"""
        return sum([1 for field in [self.dont_1, self.dont_2, self.dont_3, self.dont_4] if field.data])
    
    def calculate_journal_point(self):
        """Calculate journal point"""
        return 1 if self.journal_point.data else 0
    
    def calculate_learning_point(self):
        """Calculate learning point"""
        return 1 if self.learning_point.data else 0