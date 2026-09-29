import logging

from flask_jwt_extended import create_access_token
from marshmallow import ValidationError as MarshmallowValidationError
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User
from app.schemas import login_schema, signup_schema
from app.utils.errors import ConflictError, UnauthorizedError, UnprocessableEntityError

logger = logging.getLogger(__name__)


def _load(schema, payload: dict) -> dict:
    try:
        return schema.load(payload)
    except MarshmallowValidationError as exc:
        messages = exc.messages
        raise UnprocessableEntityError(_first_message(messages), "VALIDATION_ERROR") from exc


def _first_message(messages) -> str:
    if isinstance(messages, dict):
        for value in messages.values():
            return _first_message(value)
    if isinstance(messages, list) and messages:
        return str(messages[0])
    return str(messages)


def signup(payload: dict) -> User:
    data = _load(signup_schema, payload)
    email = data["email"].lower().strip()
    if User.query.filter_by(email=email).first():
        raise ConflictError("An account with this email already exists", "DUPLICATE_EMAIL")

    user = User(name=data["name"].strip(), email=email)
    user.set_password(data["password"])
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ConflictError("An account with this email already exists", "DUPLICATE_EMAIL") from exc

    logger.info("User signup succeeded user_id=%s email=%s", user.id, user.email)
    return user


def login(payload: dict) -> tuple[User, str]:
    data = _load(login_schema, payload)
    email = data["email"].lower().strip()
    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(data["password"]):
        logger.info("Login failed for email=%s", email)
        raise UnauthorizedError("Invalid email or password", "INVALID_CREDENTIALS")

    token = create_access_token(identity=str(user.id))
    logger.info("Login succeeded user_id=%s", user.id)
    return user, token
