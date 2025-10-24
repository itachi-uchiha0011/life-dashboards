from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from slugify import slugify
import uuid

from app.extensions import db

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    categories = db.relationship('Category', backref='owner', lazy=True, cascade='all, delete-orphan')
    pages = db.relationship('Page', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    """Category model (like workspaces in Notion)"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='📁')  # Emoji or icon class
    color = db.Column(db.String(7), default='#6366f1')  # Hex color
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    pages = db.relationship('Page', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Category, self).__init__(**kwargs)
        if not self.slug and self.title:
            self.slug = self.generate_unique_slug(self.title)
    
    def generate_unique_slug(self, title):
        """Generate unique slug for category"""
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        
        while Category.query.filter_by(slug=slug, user_id=self.user_id, is_deleted=False).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def soft_delete(self):
        """Soft delete category and all its pages"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        for page in self.pages:
            page.soft_delete()
    
    def restore(self):
        """Restore category from trash"""
        self.is_deleted = False
        self.deleted_at = None
    
    def __repr__(self):
        return f'<Category {self.title}>'

class Page(db.Model):
    """Page model for individual pages within categories"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, index=True)
    icon = db.Column(db.String(50), default='📄')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime)
    is_template = db.Column(db.Boolean, default=False)
    template_type = db.Column(db.String(50))  # 'calendar', 'habit_tracker', etc.
    
    # Foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('page.id'))  # For nested pages
    
    # Relationships
    content_blocks = db.relationship('ContentBlock', backref='page', lazy=True, 
                                   cascade='all, delete-orphan', order_by='ContentBlock.order')
    file_uploads = db.relationship('FileUpload', backref='page', lazy=True, cascade='all, delete-orphan')
    children = db.relationship('Page', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def __init__(self, **kwargs):
        super(Page, self).__init__(**kwargs)
        if not self.slug and self.title:
            self.slug = self.generate_unique_slug(self.title)
    
    def generate_unique_slug(self, title):
        """Generate unique slug for page within category"""
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        
        while Page.query.filter_by(slug=slug, category_id=self.category_id, is_deleted=False).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def soft_delete(self):
        """Soft delete page and all its content"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        # Also soft delete child pages
        for child in self.children:
            child.soft_delete()
    
    def restore(self):
        """Restore page from trash"""
        self.is_deleted = False
        self.deleted_at = None
    
    def get_content_text(self):
        """Get all content as plain text for search"""
        content_text = []
        for block in self.content_blocks:
            if block.content:
                content_text.append(block.content)
        return ' '.join(content_text)
    
    def __repr__(self):
        return f'<Page {self.title}>'

class ContentBlock(db.Model):
    """Content blocks within pages (like Notion blocks)"""
    id = db.Column(db.Integer, primary_key=True)
    block_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    block_type = db.Column(db.String(50), nullable=False)  # 'text', 'heading', 'todo', 'image', etc.
    content = db.Column(db.Text)
    metadata = db.Column(db.JSON)  # Store additional data like todo status, heading level, etc.
    order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    
    def __repr__(self):
        return f'<ContentBlock {self.block_type}: {self.block_id}>'

class FileUpload(db.Model):
    """File uploads associated with pages"""
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Stored filename
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    is_image = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='file_uploads')
    
    def __repr__(self):
        return f'<FileUpload {self.original_filename}>'