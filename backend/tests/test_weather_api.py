# backend/tests/test_weather_api.py
from __future__ import annotations


def _weather_base_path(client) -> str:
    trial = client.get("/api/v1/weather")
    if trial.status_code != 404:
        return "/api/v1/weather"
    return "/api/v1/weather/"


def test_create_weather(client, weather_payload_1):
    base = _weather_base_path(client)

    response = client.post(base, json=weather_payload_1)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["id"] > 0
    assert data["year"] == 2009
    assert data["temperature_c"] == 18.5
    assert data["dataset_name"] == "unit-test-weather"


def test_list_weather_and_filter_by_year(client, create_weather, weather_payload_1, weather_payload_2, weather_payload_3):
    base = _weather_base_path(client)

    create_weather(weather_payload_1)
    create_weather(weather_payload_2)
    create_weather(weather_payload_3)

    response = client.get(base, params={"year": 2009})
    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) >= 2
    assert all(item["year"] == 2009 for item in data)


def test_get_weather_by_id(client, create_weather, weather_payload_1):
    created = create_weather(weather_payload_1)

    response = client.get(f"/api/v1/weather/{created['id']}")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == created["id"]
    assert data["source"] == weather_payload_1["source"]


def test_weather_update_method_is_not_supported(client, create_weather, weather_payload_1):
    created = create_weather(weather_payload_1)

    update_payload = {
        "observed_at": "2009-07-01T10:30:00Z",
        "latitude": 53.8010,
        "longitude": -1.5510,
        "year": 2009,
        "temperature_c": 20.4,
        "precipitation_mm": 0.6,
        "wind_u": 0.9,
        "wind_v": 0.1,
        "surface_pressure": 1010.5,
        "source": "test-updated",
        "dataset_name": "unit-test-weather-updated",
    }

    response = client.put(f"/api/v1/weather/{created['id']}", json=update_payload)
    assert response.status_code == 405, response.text

def test_delete_weather(client, create_weather, weather_payload_1):
    created = create_weather(weather_payload_1)

    response = client.delete(f"/api/v1/weather/{created['id']}")
    assert response.status_code == 204, response.text

    get_response = client.get(f"/api/v1/weather/{created['id']}")
    assert get_response.status_code in {404, 422}, get_response.text


def test_weather_coverage_summary(client, create_weather, weather_payload_1, weather_payload_2, weather_payload_3):
    create_weather(weather_payload_1)
    create_weather(weather_payload_2)
    create_weather(weather_payload_3)

    response = client.get("/api/v1/weather/coverage/summary")
    assert response.status_code == 200, response.text

    data = response.json()
    assert "available_years" in data
    assert "total_records" in data
    assert "earliest_timestamp" in data
    assert "latest_timestamp" in data
    assert 2009 in data["available_years"]
    assert 2010 in data["available_years"]
    assert data["total_records"] >= 3


def test_weather_validation_rejects_invalid_latitude(client, weather_payload_1):
    base = _weather_base_path(client)

    invalid_payload = dict(weather_payload_1)
    invalid_payload["latitude"] = -95.0

    response = client.post(base, json=invalid_payload)
    assert response.status_code == 422, response.text
    assert "detail" in response.json()


def test_weather_validation_rejects_invalid_longitude(client, weather_payload_1):
    base = _weather_base_path(client)

    invalid_payload = dict(weather_payload_1)
    invalid_payload["longitude"] = 181.0

    response = client.post(base, json=invalid_payload)
    assert response.status_code == 422, response.text
    assert "detail" in response.json()


def test_weather_allows_nullable_source(client, weather_payload_1):
    base = _weather_base_path(client)

    payload = dict(weather_payload_1)
    payload.pop("source")

    response = client.post(base, json=payload)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["dataset_name"] == weather_payload_1["dataset_name"]
    assert data["source"] is None