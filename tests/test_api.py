import pytest


def test_add_tracked_country_without_data(test_client):
    assert test_client.post("/tracked").status_code >= 400


# @pytest.mark.skip("Figure how to use empty test database")
def test_add_tracked_country(test_client):
    response = test_client.post("/tracked", json={"country_codes": ["PL"]})
    assert response.status_code == 201
    date = "2020-09-24"
    response = test_client.get(f"/tracked/{date}")
    assert response.json.get("date", None) == date
    added_country = next(
        (c for c in response.json.get("countries") if c["Country"] == "Poland"), None,
    )
    assert added_country
    assert all(key in added_country for key in ("Active", "Deaths", "Recovered"))
