from app.models import DiagnosticCentre, DiagnosticTest
from app.services import cache_service
from app.utils.errors import NotFoundError


def list_centres(page: int, per_page: int) -> tuple[list[dict], dict]:
    cache_key = cache_service.centres_list_key(page, per_page)
    cached = cache_service.get_json(cache_key)
    if cached:
        return cached["data"], cached["meta"]

    query = DiagnosticCentre.query.order_by(DiagnosticCentre.id.asc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    data = [centre.to_dict() for centre in pagination.items]
    meta = {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }
    cache_service.set_json(cache_key, {"data": data, "meta": meta})
    return data, meta


def get_centre(centre_id: int, include_tests: bool = False) -> dict:
    centre = DiagnosticCentre.query.get(centre_id)
    if centre is None:
        raise NotFoundError("Diagnostic centre not found.", "CENTRE_NOT_FOUND")
    return centre.to_dict(include_tests=include_tests)


def list_centre_tests(centre_id: int) -> list[dict]:
    centre = DiagnosticCentre.query.get(centre_id)
    if centre is None:
        raise NotFoundError("Diagnostic centre not found.", "CENTRE_NOT_FOUND")
    cache_key = cache_service.centre_tests_key(centre_id)
    cached = cache_service.get_json(cache_key)
    if cached is not None:
        return cached
    data = [test.to_dict() for test in centre.tests]
    cache_service.set_json(cache_key, data)
    return data


def get_test(test_id: int) -> dict:
    test = DiagnosticTest.query.get(test_id)
    if test is None:
        raise NotFoundError("Diagnostic test not found.", "TEST_NOT_FOUND")
    return test.to_dict()
