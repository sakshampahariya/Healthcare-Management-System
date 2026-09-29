from decimal import Decimal

from app.extensions import db
from app.models.base import TimestampMixin


class DiagnosticTest(TimestampMixin, db.Model):
    __tablename__ = "diagnostic_tests"

    id = db.Column(db.Integer, primary_key=True)
    centre_id = db.Column(
        db.Integer,
        db.ForeignKey("diagnostic_centres.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    centre = db.relationship("DiagnosticCentre", back_populates="tests")
    bookings = db.relationship("Booking", back_populates="test", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "centre_id": self.centre_id,
            "name": self.name,
            "description": self.description,
            "price": str(Decimal(self.price)),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
