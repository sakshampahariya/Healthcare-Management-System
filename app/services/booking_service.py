import logging
from datetime import datetime, timezone

from marshmallow import ValidationError as MarshmallowValidationError

from app.constants import BOOKING_CANCELLED, BOOKING_PENDING
from app.extensions import db
from app.models import Booking, DiagnosticCentre, DiagnosticTest
from app.schemas import create_booking_schema
from app.utils.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)

logger = logging.getLogger(__name__)


def _load_booking_payload(payload: dict) -> dict:
    try:
        return create_booking_schema.load(payload)
    except MarshmallowValidationError as exc:
        raise UnprocessableEntityError(
            "Invalid booking payload", "VALIDATION_ERROR"
        ) from exc


def get_owned_booking(booking_id: int, user_id: int, *, for_update: bool = False) -> Booking:
    query = db.session.query(Booking).filter(Booking.id == booking_id)
    if for_update:
        query = query.with_for_update()
    booking = query.first()
    if booking is None:
        raise NotFoundError("Booking not found", "BOOKING_NOT_FOUND")
    if booking.user_id != user_id:
        raise ForbiddenError("You cannot access another user's booking", "BOOKING_FORBIDDEN")
    return booking


def create_booking(user_id: int, payload: dict) -> Booking:
    data = _load_booking_payload(payload)
    centre = db.session.get(DiagnosticCentre, data["centre_id"])
    if centre is None:
        raise NotFoundError("Diagnostic centre not found", "CENTRE_NOT_FOUND")

    test = db.session.get(DiagnosticTest, data["test_id"])
    if test is None:
        raise NotFoundError("Diagnostic test not found", "TEST_NOT_FOUND")

    if test.centre_id != centre.id:
        raise UnprocessableEntityError(
            "Test does not belong to the selected centre",
            "TEST_CENTRE_MISMATCH",
        )

    appointment = data["appointment_datetime"]
    if appointment.tzinfo is None:
        appointment = appointment.replace(tzinfo=timezone.utc)
    if appointment <= datetime.now(timezone.utc):
        raise UnprocessableEntityError(
            "Appointment datetime must be in the future",
            "INVALID_APPOINTMENT",
        )

    booking = Booking(
        user_id=user_id,
        test_id=test.id,
        centre_id=centre.id,
        appointment_datetime=appointment,
        amount=test.price,
        status=BOOKING_PENDING,
    )
    db.session.add(booking)
    db.session.commit()
    logger.info(
        "Booking created booking_id=%s user_id=%s test_id=%s amount=%s",
        booking.id,
        user_id,
        test.id,
        booking.amount,
    )
    return booking


def list_bookings(user_id: int, page: int, per_page: int):
    query = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination.items, {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }


def cancel_booking(user_id: int, booking_id: int) -> Booking:
    booking = get_owned_booking(booking_id, user_id, for_update=True)
    if booking.status != BOOKING_PENDING:
        raise ConflictError(
            "Only pending bookings can be cancelled",
            "BOOKING_NOT_CANCELLABLE",
        )
    booking.status = BOOKING_CANCELLED
    db.session.commit()
    logger.info("Booking cancelled booking_id=%s user_id=%s", booking.id, user_id)
    return booking
