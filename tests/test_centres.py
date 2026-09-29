def test_list_centres(client, centre):
    response = client.get("/api/centres")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["meta"]["total"] == 1
    assert body["data"][0]["name"] == "EVE Koramangala"


def test_retrieve_centre_tests(client, centre, diagnostic_test):
    response = client.get(f"/api/centres/{centre.id}/tests")
    assert response.status_code == 200
    tests = response.get_json()["data"]
    assert len(tests) == 1
    assert tests[0]["name"] == "CBC"
    assert tests[0]["price"] == "499.00"


def test_invalid_centre_id(client):
    response = client.get("/api/centres/9999")
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "CENTRE_NOT_FOUND"


def test_get_test(client, diagnostic_test):
    response = client.get(f"/api/tests/{diagnostic_test.id}")
    assert response.status_code == 200
    assert response.get_json()["data"]["id"] == diagnostic_test.id


def test_centres_pagination_meta(client, centre, other_centre):
    response = client.get("/api/centres?page=1&per_page=1")
    body = response.get_json()
    assert body["meta"]["page"] == 1
    assert body["meta"]["per_page"] == 1
    assert body["meta"]["total"] == 2
    assert len(body["data"]) == 1
