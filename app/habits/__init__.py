from flask import Blueprint

habits_bp = Blueprint("habits", __name__, url_prefix="/habits")

from . import routes  # noqa: E402,F401