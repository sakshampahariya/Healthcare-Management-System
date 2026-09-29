from app.extensions import db
from app.models.base import TimestampMixin


class DiagnosticCentre(TimestampMixin, db.Model):
    __tablename__ = "diagnostic_centres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(255), nullable=False)

    tests = db.relationship(
        "DiagnosticTest",
        back_populates="centre",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    bookings = db.relationship("Booking", back_populates="centre", lazy="dynamic")

    def to_dict(self, include_tests: bool = False) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_tests:
            data["tests"] = [test.to_dict() for test in self.tests]
        return data
