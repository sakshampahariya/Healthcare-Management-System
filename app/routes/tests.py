from flask import Blueprint

from app.services import catalogue_service
from app.utils.responses import success_response

tests_bp = Blueprint("tests", __name__, url_prefix="/api/tests")


@tests_bp.get("/<int:test_id>")
def get_test(test_id: int):
    test = catalogue_service.get_test(test_id)
    return success_response(test.to_dict())
