from flask import Blueprint

from app.services import catalogue_service
from app.utils.responses import success_response
from app.utils.validators import parse_pagination

centres_bp = Blueprint("centres", __name__, url_prefix="/api/centres")


@centres_bp.get("")
def list_centres():
    page, per_page = parse_pagination()
    data, meta, _cached = catalogue_service.list_centres(page, per_page)
    return success_response(data, meta=meta)


@centres_bp.get("/<int:centre_id>")
def get_centre(centre_id: int):
    centre = catalogue_service.get_centre(centre_id)
    return success_response(centre.to_dict(include_tests=True))


@centres_bp.get("/<int:centre_id>/tests")
def list_centre_tests(centre_id: int):
    _centre, tests, _cached = catalogue_service.list_centre_tests(centre_id)
    return success_response(tests)
