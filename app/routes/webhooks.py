from flask import Blueprint

from app.services import webhook_service
from app.utils.responses import success_response
from app.utils.validators import json_body

webhooks_bp = Blueprint("webhooks", __name__, url_prefix="/api/payments")


@webhooks_bp.post("/webhook/")
@webhooks_bp.post("/webhook")
def payment_webhook():
    result = webhook_service.process_webhook(json_body())
    return success_response(result)
