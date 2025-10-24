"""Compatibility launcher.

This top-level `app.py` used to contain a second, conflicting app factory and
duplicate route registrations. That caused endpoints and URL prefixes to be
inconsistent with the package-based application in `app/` (for example
`/category` vs `/categories`, and different `categories` endpoints), which made
navigation (Categories, Calendar, Trash, Backups, Settings) fail depending on
how the app was started.

To ensure running `python app.py` behaves the same as `python run.py` or using
the `app` package, we now import and run the packaged factory (`app.create_app`).
"""

from app import create_app


def main():
    app = create_app()

    # Create database tables if needed (no-op if already managed elsewhere)
    with app.app_context():
        try:
            from app.extensions import db
            db.create_all()
        except Exception:
            # don't fail startup for minor DB create issues here
            pass

    app.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    main()