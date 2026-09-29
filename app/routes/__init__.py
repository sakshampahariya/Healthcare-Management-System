from flask import Blueprint

from app.routes.auth import auth_bp
from app.routes.bookings import bookings_bp
from app.routes.centres import centres_bp
from app.routes.payments import payments_bp
from app.routes.tests import tests_bp
from app.routes.webhooks import webhooks_bp
from app.utils.responses import success_response

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health():
    return success_response({"status": "ok"})


def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(centres_bp)
    app.register_blueprint(tests_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(webhooks_bp)
