import logging

from flask import current_app
from flask_mail import Message

from app.extensions import celery, mail

logger = logging.getLogger(__name__)


def _build_confirmation_email(booking) -> Message:
    """Build a booking confirmation email with both plain-text and HTML parts."""
    user = booking.user
    test = booking.test
    centre = booking.centre
    appt = booking.appointment_datetime.strftime("%d %b %Y at %I:%M %p") if booking.appointment_datetime else "N/A"

    subject = f"EVE Healthcare – Booking Confirmed (#{booking.id})"

    text_body = (
        f"Hi {user.name},\n\n"
        f"Your booking has been confirmed!\n\n"
        f"  Booking ID   : #{booking.id}\n"
        f"  Test         : {test.name}\n"
        f"  Centre       : {centre.name}\n"
        f"  Location     : {centre.location}\n"
        f"  Appointment  : {appt}\n"
        f"  Amount Paid  : ₹{booking.amount}\n\n"
        f"Please arrive 15 minutes early with a valid photo ID.\n\n"
        f"Thank you for choosing EVE Healthcare.\n"
    )

    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <style>
        body {{ font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 40px auto; background: #ffffff;
                      border-radius: 8px; overflow: hidden;
                      box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .header {{ background: #1d4ed8; padding: 32px 40px; text-align: center; }}
        .header h1 {{ color: #ffffff; margin: 0; font-size: 22px; letter-spacing: 0.5px; }}
        .header p  {{ color: #bfdbfe; margin: 6px 0 0; font-size: 14px; }}
        .body {{ padding: 36px 40px; }}
        .body h2 {{ color: #1e293b; margin-top: 0; font-size: 18px; }}
        .body p  {{ color: #475569; line-height: 1.6; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 24px 0; }}
        .table td {{ padding: 10px 14px; border-bottom: 1px solid #e2e8f0;
                     color: #1e293b; font-size: 14px; }}
        .table td:first-child {{ font-weight: 600; width: 40%; color: #64748b; }}
        .badge {{ display: inline-block; background: #dcfce7; color: #15803d;
                  padding: 4px 12px; border-radius: 20px; font-size: 13px;
                  font-weight: 700; margin-bottom: 20px; }}
        .footer {{ background: #f8fafc; padding: 20px 40px; text-align: center;
                   font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>EVE Healthcare</h1>
          <p>Your health, confirmed.</p>
        </div>
        <div class="body">
          <span class="badge">✓ Booking Confirmed</span>
          <h2>Hi {user.name}, you're all set!</h2>
          <p>Your diagnostic test has been booked and payment received. Here are your details:</p>
          <table class="table">
            <tr><td>Booking ID</td><td>#{booking.id}</td></tr>
            <tr><td>Test</td><td>{test.name}</td></tr>
            <tr><td>Centre</td><td>{centre.name}</td></tr>
            <tr><td>Location</td><td>{centre.location}</td></tr>
            <tr><td>Appointment</td><td>{appt}</td></tr>
            <tr><td>Amount Paid</td><td>₹{booking.amount}</td></tr>
          </table>
          <p>Please arrive <strong>15 minutes early</strong> with a valid photo ID.</p>
          <p>If you have any questions, reply to this email or contact our support team.</p>
          <p style="margin-top:32px; color:#1e293b;">Warm regards,<br/><strong>EVE Healthcare Team</strong></p>
        </div>
        <div class="footer">
          © 2025 EVE Healthcare. All rights reserved.<br/>
          This is an automated message – please do not reply directly.
        </div>
      </div>
    </body>
    </html>
    """

    msg = Message(
        subject=subject,
        recipients=[user.email],
        body=text_body,
        html=html_body,
    )
    return msg


@celery.task(name="send_booking_confirmation", bind=True, max_retries=3, default_retry_delay=30)
def send_booking_confirmation(self, booking_id: int) -> str:
    """Send a booking confirmation email to the user.

    Retries up to 3 times (30-second delay) if SMTP fails.
    """
    from app.extensions import db
    from app.models import Booking

    try:
        booking = (
            db.session.query(Booking)
            .filter_by(id=booking_id)
            .first()
        )

        if booking is None:
            logger.warning("send_booking_confirmation: booking #%s not found – skipping.", booking_id)
            return f"Booking #{booking_id} not found – email skipped."

        if not booking.user or not booking.user.email:
            logger.warning("send_booking_confirmation: no email for booking #%s – skipping.", booking_id)
            return f"No user email for booking #{booking_id} – email skipped."

        msg = _build_confirmation_email(booking)
        mail.send(msg)

        message = f"Booking confirmation sent for booking #{booking_id}"
        logger.info(message)
        return message

    except Exception as exc:
        logger.error(
            "send_booking_confirmation failed for booking #%s: %s",
            booking_id,
            exc,
            exc_info=True,
        )
        raise self.retry(exc=exc)
