import logging
import random
import uuid

from flask import current_app
from marshmallow import ValidationError as MarshmallowValidationError

from app.constants import (
    BOOKING_CANCELLED,
    BOOKING_CONFIRMED,
    BOOKING_FAILED,
    PAYMENT_FAILED,
    PAYMENT_SUCCESS,
)
from app.extensions import db
from app.models import Payment
from app.schemas import create_payment_schema
from app.services.booking_service import get_owned_booking
from app.utils.errors import ConflictError, UnprocessableEntityError

logger = logging.getLogger(__name__)


def _load_payment_payload(payload: dict) -> dict:
    try:
        return create_payment_schema.load(payload)
    except MarshmallowValidationError as exc:
        raise UnprocessableEntityError("Invalid payment payload", "VALIDATION_ERROR") from exc


def resolve_simulation_result(requested: str | None) -> str:
    if requested in (PAYMENT_SUCCESS, PAYMENT_FAILED):
        return requested
    configured = current_app.config.get("PAYMENT_SIMULATE_RESULT", PAYMENT_SUCCESS)
    if configured == "RANDOM":
        return random.choice([PAYMENT_SUCCESS, PAYMENT_FAILED])
    if configured in (PAYMENT_SUCCESS, PAYMENT_FAILED):
        return configured
    return PAYMENT_SUCCESS


def apply_payment_result(booking, payment: Payment, result: str) -> None:
    """Update payment + booking together. Caller owns the transaction."""
    payment.status = result
    if result == PAYMENT_SUCCESS:
        if booking.status != BOOKING_CANCELLED:
            booking.status = BOOKING_CONFIRMED
    elif result == PAYMENT_FAILED:
        if booking.status not in (BOOKING_CONFIRMED, BOOKING_CANCELLED):
            booking.status = BOOKING_FAILED


def enqueue_confirmation(booking_id: int) -> None:
    from app.tasks.payment_tasks import send_booking_confirmation

    send_booking_confirmation.delay(booking_id)


def create_simulated_payment(user_id: int, payload: dict) -> Payment:
    data = _load_payment_payload(payload)
    booking = get_owned_booking(data["booking_id"], user_id, for_update=True)

    if booking.status == BOOKING_CANCELLED:
        raise ConflictError("Cannot pay for a cancelled booking", "BOOKING_CANCELLED")

    existing_success = (
        Payment.query.filter_by(booking_id=booking.id, status=PAYMENT_SUCCESS)
        .with_for_update()
        .first()
    )
    if existing_success or booking.status == BOOKING_CONFIRMED:
        raise ConflictError(
            "A successful payment already exists for this booking",
            "PAYMENT_ALREADY_SUCCEEDED",
        )

    result = resolve_simulation_result(data.get("simulate_result"))
    payment = Payment(
        booking_id=booking.id,
        external_payment_id=f"pay_{uuid.uuid4().hex}",
        amount=booking.amount,
        status=result,
    )
    db.session.add(payment)
    apply_payment_result(booking, payment, result)
    db.session.commit()

    logger.info(
        "Payment attempt payment_id=%s booking_id=%s result=%s amount=%s",
        payment.external_payment_id,
        booking.id,
        result,
        payment.amount,
    )
    if result == PAYMENT_SUCCESS:
        logger.info("Payment succeeded booking_id=%s", booking.id)
        enqueue_confirmation(booking.id)
    else:
        logger.info("Payment failed booking_id=%s", booking.id)

    return payment
