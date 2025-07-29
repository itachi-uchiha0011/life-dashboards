from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from models import User, Category, Page

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