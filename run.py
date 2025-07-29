#!/usr/bin/env python3
"""
Simple script to run the Notion Clone Flask application
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    from app import create_app
    from models import User, Category, Page, ContentBlock, FileUpload
    
    app = create_app()
    
    # Create database tables
    with app.app_context():
        try:
            from app import db
            db.create_all()
            print("✓ Database tables created successfully!")
        except Exception as e:
            print(f"✗ Error creating database tables: {e}")
            sys.exit(1)
    
    print("🚀 Starting Notion Clone Flask App...")
    print("📱 Open your browser and navigate to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thank you for using Notion Clone!")