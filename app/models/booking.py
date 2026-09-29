from decimal import Decimal

from app.constants import BOOKING_PENDING
from app.extensions import db
from app.models.base import UpdateTimestampMixin


class Booking(UpdateTimestampMixin, db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_id = db.Column(
        db.Integer,
        db.ForeignKey("diagnostic_tests.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    centre_id = db.Column(
        db.Integer,
        db.ForeignKey("diagnostic_centres.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    appointment_datetime = db.Column(db.DateTime(timezone=True), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=BOOKING_PENDING, index=True)

    user = db.relationship("User", back_populates="bookings")
    test = db.relationship("DiagnosticTest", back_populates="bookings")
    centre = db.relationship("DiagnosticCentre", back_populates="bookings")
    payments = db.relationship("Payment", back_populates="booking", lazy="selectin")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "test_id": self.test_id,
            "centre_id": self.centre_id,
            "appointment_datetime": (
                self.appointment_datetime.isoformat() if self.appointment_datetime else None
            ),
            "amount": str(Decimal(self.amount)),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
