import os
from app import create_app

# Create app instance
app = create_app()

# Run database migrations on startup
with app.app_context():
    try:
        from flask_migrate import upgrade
        upgrade()
        print("Database migrations completed successfully")
    except Exception as e:
        print(f"Database migration error: {e}")
        # Continue anyway for development

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)