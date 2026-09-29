import re

from marshmallow import EXCLUDE, Schema, fields, validate, validates, ValidationError


PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE


class SignupSchema(BaseSchema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True)

    @validates("password")
    def validate_password(self, value, **kwargs):
        if not PASSWORD_PATTERN.match(value):
            raise ValidationError(
                "Password must be at least 8 characters and include a letter and a number."
            )


class LoginSchema(BaseSchema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


class CreateBookingSchema(BaseSchema):
    test_id = fields.Integer(required=True, validate=validate.Range(min=1))
    centre_id = fields.Integer(required=True, validate=validate.Range(min=1))
    appointment_datetime = fields.DateTime(required=True)


class CreatePaymentSchema(BaseSchema):
    booking_id = fields.Integer(required=True, validate=validate.Range(min=1))
    simulate_result = fields.String(
        required=False,
        validate=validate.OneOf(["SUCCESS", "FAILED"]),
        load_default=None,
    )


class WebhookSchema(BaseSchema):
    event_id = fields.String(required=True, validate=validate.Length(min=1, max=128))
    payment_id = fields.String(required=True, validate=validate.Length(min=1, max=64))
    status = fields.String(required=True, validate=validate.OneOf(["SUCCESS", "FAILED"]))


signup_schema = SignupSchema()
login_schema = LoginSchema()
create_booking_schema = CreateBookingSchema()
create_payment_schema = CreatePaymentSchema()
webhook_schema = WebhookSchema()
