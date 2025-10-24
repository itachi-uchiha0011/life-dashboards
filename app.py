import os
from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
import secrets

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///notion_clone.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.categories import categories_bp
    from routes.pages import pages_bp
    from routes.api import api_bp
    from app.drive.routes import drive_bp
    from app.tasks.routes import tasks_bp
    from app.dashboard.routes import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(categories_bp, url_prefix='/category')
    app.register_blueprint(pages_bp, url_prefix='/page')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(drive_bp)
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    # Context processor for theme and CSRF
    @app.context_processor
    def inject_theme():
        from flask_wtf.csrf import generate_csrf
        return {
            'current_theme': session.get('theme', 'light'),
            'csrf_token': generate_csrf
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from models import User, Category, Page, ContentBlock, FileUpload
        db.create_all()
    app.run(debug=True)