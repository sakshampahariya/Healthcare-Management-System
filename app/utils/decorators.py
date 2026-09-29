"""Shared route helpers. Ownership checks live in services, not here."""

from functools import wraps

from flask_jwt_extended import get_jwt_identity, jwt_required

from app.utils.errors import UnauthorizedError


def current_user_id() -> int:
    identity = get_jwt_identity()
    if identity is None:
        raise UnauthorizedError()
    return int(identity)


def login_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper
