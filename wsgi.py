import os
from app import create_app

# Create app instance
app = create_app()

# Run database migrations on startup
with app.app_context():
    try:
        from flask_migrate import upgrade, init, migrate
        from flask_sqlalchemy import SQLAlchemy
        from app.extensions import db
        
        # Check if database exists and is accessible
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            print("Database connection successful")
        except Exception as db_error:
            print(f"Database connection error: {db_error}")
            # Try to create database if it doesn't exist
            try:
                db.create_all()
                print("Database tables created successfully")
            except Exception as create_error:
                print(f"Failed to create database tables: {create_error}")
                # Don't raise error, continue with app startup
                print("Continuing without database initialization...")
        
        # Run migrations
        try:
            upgrade()
            print("Database migrations completed successfully")
        except Exception as migrate_error:
            print(f"Migration error: {migrate_error}")
            # If migrations fail, try to create tables directly
            try:
                db.create_all()
                print("Database tables created directly (migration fallback)")
            except Exception as create_error:
                print(f"Failed to create tables as fallback: {create_error}")
                # Continue anyway for development
                print("Continuing without database initialization...")
                
    except Exception as e:
        print(f"Database initialization error: {e}")
        # Continue anyway for development
        print("Continuing without database initialization...")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)