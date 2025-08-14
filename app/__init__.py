from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager, scheduler, csrf
from .models import User


def create_app(config_class: type[Config] | None = None) -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_class or Config)

    # Enable CSRF
    app.config.setdefault("WTF_CSRF_TIME_LIMIT", None)
    csrf.init_app(app)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from .auth.routes import auth_bp
    from .dashboard.routes import dashboard_bp
    from .habits.routes import habits_bp
    from .journal.routes import journal_bp
    from .categories.routes import categories_bp
    from .files.routes import files_bp
    from .exports.routes import exports_bp
    from .api.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Start scheduler
    with app.app_context():
        from .jobs import schedule_jobs
        schedule_jobs()
        if not scheduler.running:
            scheduler.start()

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    return app