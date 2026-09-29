from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.services import booking_service
from app.utils.decorators import current_user_id
from app.utils.responses import success_response
from app.utils.validators import json_body, parse_pagination

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")


@bookings_bp.post("")
@jwt_required()
def create_booking():
    booking = booking_service.create_booking(current_user_id(), json_body())
    return success_response(booking.to_dict(), status=201)


@bookings_bp.get("")
@jwt_required()
def list_bookings():
    page, per_page = parse_pagination()
    items, meta = booking_service.list_bookings(current_user_id(), page, per_page)
    return success_response([booking.to_dict() for booking in items], meta=meta)


@bookings_bp.get("/<int:booking_id>")
@jwt_required()
def get_booking(booking_id: int):
    booking = booking_service.get_owned_booking(booking_id, current_user_id())
    return success_response(booking.to_dict())


@bookings_bp.post("/<int:booking_id>/cancel")
@jwt_required()
def cancel_booking(booking_id: int):
    booking = booking_service.cancel_booking(current_user_id(), booking_id)
    return success_response(booking.to_dict())
