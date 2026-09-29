from app.extensions import db
from app.models import DiagnosticCentre, DiagnosticTest
from app.services.cache_service import (
    cache_get,
    cache_set,
    centre_tests_key,
    centres_list_key,
)
from app.utils.errors import NotFoundError


def list_centres(page: int, per_page: int):
    key = centres_list_key(page, per_page)
    cached = cache_get(key)
    if cached is not None:
        return cached["data"], cached["meta"], True

    pagination = DiagnosticCentre.query.order_by(DiagnosticCentre.id.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    data = [centre.to_dict() for centre in pagination.items]
    meta = {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }
    cache_set(key, {"data": data, "meta": meta})
    return data, meta, False


def get_centre(centre_id: int) -> DiagnosticCentre:
    centre = db.session.get(DiagnosticCentre, centre_id)
    if centre is None:
        raise NotFoundError("Diagnostic centre not found", "CENTRE_NOT_FOUND")
    return centre


def list_centre_tests(centre_id: int):
    centre = get_centre(centre_id)
    key = centre_tests_key(centre.id)
    cached = cache_get(key)
    if cached is not None:
        return centre, cached, True

    tests = [test.to_dict() for test in centre.tests]
    cache_set(key, tests)
    return centre, tests, False


def get_test(test_id: int) -> DiagnosticTest:
    test = db.session.get(DiagnosticTest, test_id)
    if test is None:
        raise NotFoundError("Diagnostic test not found", "TEST_NOT_FOUND")
    return test
