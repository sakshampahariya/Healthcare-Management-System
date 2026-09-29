import logging

from marshmallow import ValidationError as MarshmallowValidationError
from sqlalchemy.exc import IntegrityError

from app.constants import PAYMENT_FAILED, PAYMENT_SUCCESS
from app.extensions import db
from app.models import Booking, Payment, WebhookEvent
from app.schemas import webhook_schema
from app.services.payment_service import apply_payment_result, enqueue_confirmation
from app.utils.errors import NotFoundError, UnprocessableEntityError

logger = logging.getLogger(__name__)


def _load_webhook(payload: dict) -> dict:
    try:
        return webhook_schema.load(payload)
    except MarshmallowValidationError as exc:
        raise UnprocessableEntityError("Invalid webhook payload", "VALIDATION_ERROR") from exc


def process_webhook(payload: dict) -> dict:
    data = _load_webhook(payload)
    event_id = data["event_id"]
    external_payment_id = data["payment_id"]
    status = data["status"]

    logger.info(
        "Webhook received event_id=%s payment_id=%s status=%s",
        event_id,
        external_payment_id,
        status,
    )

    event = WebhookEvent(
        event_id=event_id,
        external_payment_id=external_payment_id,
        event_type=status,
        processed=False,
    )
    db.session.add(event)
    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        logger.info("Duplicate webhook detected event_id=%s", event_id)
        existing = WebhookEvent.query.filter_by(event_id=event_id).first()
        return {
            "already_processed": True,
            "event_id": event_id,
            "processed": bool(existing.processed) if existing else True,
        }

    payment = (
        db.session.query(Payment)
        .filter_by(external_payment_id=external_payment_id)
        .with_for_update()
        .first()
    )
    if payment is None:
        db.session.rollback()
        raise NotFoundError("Payment not found for webhook", "PAYMENT_NOT_FOUND")

    booking = (
        db.session.query(Booking)
        .filter_by(id=payment.booking_id)
        .with_for_update()
        .first()
    )

    previous_payment_status = payment.status
    should_apply = status == PAYMENT_SUCCESS or (
        status == PAYMENT_FAILED and previous_payment_status != PAYMENT_SUCCESS
    )
    if should_apply:
        apply_payment_result(booking, payment, status)

    event.processed = True
    db.session.commit()

    if status == PAYMENT_SUCCESS and previous_payment_status != PAYMENT_SUCCESS:
        enqueue_confirmation(booking.id)

    logger.info(
        "Webhook processed event_id=%s payment_id=%s status=%s",
        event_id,
        external_payment_id,
        status,
    )
    return {
        "already_processed": False,
        "event_id": event_id,
        "payment": payment.to_dict(),
        "booking_status": booking.status,
        "processed": True,
    }
