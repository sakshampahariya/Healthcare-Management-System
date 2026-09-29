from app.extensions import db
from app.models.base import TimestampMixin


class WebhookEvent(TimestampMixin, db.Model):
    __tablename__ = "webhook_events"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(128), nullable=False, unique=True, index=True)
    external_payment_id = db.Column(db.String(64), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False)
    processed = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_id": self.event_id,
            "external_payment_id": self.external_payment_id,
            "event_type": self.event_type,
            "processed": self.processed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
