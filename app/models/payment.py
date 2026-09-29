from decimal import Decimal

from sqlalchemy import Index, text

from app.constants import PAYMENT_PENDING
from app.extensions import db
from app.models.base import UpdateTimestampMixin


class Payment(UpdateTimestampMixin, db.Model):
    __tablename__ = "payments"
    __table_args__ = (
        Index(
            "uq_payments_one_success_per_booking",
            "booking_id",
            unique=True,
            postgresql_where=text("status = 'SUCCESS'"),
            sqlite_where=text("status = 'SUCCESS'"),
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    external_payment_id = db.Column(db.String(64), nullable=False, unique=True, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=PAYMENT_PENDING, index=True)

    booking = db.relationship("Booking", back_populates="payments")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "external_payment_id": self.external_payment_id,
            "amount": str(Decimal(self.amount)),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
