from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.services import payment_service
from app.utils.decorators import current_user_id
from app.utils.responses import success_response
from app.utils.validators import json_body

payments_bp = Blueprint("payments", __name__, url_prefix="/api/payments")


@payments_bp.post("/")
@payments_bp.post("")
@jwt_required()
def create_payment():
    payment = payment_service.create_simulated_payment(current_user_id(), json_body())
    return success_response(
        {
            "payment": payment.to_dict(),
            "booking_status": payment.booking.status,
        },
        status=201,
    )
