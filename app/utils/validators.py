from datetime import datetime
from functools import wraps

from flask import request

from app.utils.errors import BadRequestError


def parse_pagination(default_per_page: int = 10, max_per_page: int = 50):
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", default_per_page))
    except (TypeError, ValueError) as exc:
        raise BadRequestError("page and per_page must be integers", "INVALID_PAGINATION") from exc
    if page < 1 or per_page < 1:
        raise BadRequestError("page and per_page must be >= 1", "INVALID_PAGINATION")
    per_page = min(per_page, max_per_page)
    return page, per_page


def json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BadRequestError("JSON body is required", "INVALID_JSON")
    return data


def require_json(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        json_body()
        return fn(*args, **kwargs)

    return wrapper


def parse_iso_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise BadRequestError("Invalid datetime format. Use ISO 8601.", "INVALID_DATETIME") from exc
