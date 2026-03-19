# backend/tests/test_trackpoints_api.py
from __future__ import annotations


def test_create_trackpoint(client, create_gull, gull_payload):
    gull = create_gull(gull_payload)

    payload = {
        "gull_id": gull["id"],
        "recorded_at": "2009-07-01T10:05:00Z",
        "latitude": 53.8000,
        "longitude": -1.5500,
        "event_id": "TRACK-1",
        "sensor_type": "gps",
        "visible": "true",
    }

    response = client.post("/api/v1/trackpoints", json=payload)
    if response.status_code == 404:
        response = client.post("/api/v1/trackpoints/", json=payload)

    assert response.status_code == 201, response.text
    data = response.json()

    assert data["id"] > 0
    assert data["gull_id"] == gull["id"]
    assert data["event_id"] == "TRACK-1"


def test_create_trackpoint_with_nonexistent_gull_id_fails(client):
    payload = {
        "gull_id": 999999,
        "recorded_at": "2009-07-01T10:05:00Z",
        "latitude": 53.8000,
        "longitude": -1.5500,
        "event_id": "BAD-FK",
        "sensor_type": "gps",
        "visible": "true",
    }

    response = client.post("/api/v1/trackpoints", json=payload)
    if response.status_code == 404:
        response = client.post("/api/v1/trackpoints/", json=payload)

    assert response.status_code == 404, response.text
    assert "not found" in response.json()["detail"].lower()


def test_list_trackpoints_and_filter_by_gull_id(
    client, create_gull, create_trackpoint, gull_payload, second_gull_payload
):
    gull_a = create_gull(gull_payload)
    gull_b = create_gull(second_gull_payload)

    tp_a = create_trackpoint(
        {
            "gull_id": gull_a["id"],
            "recorded_at": "2009-07-01T10:05:00Z",
            "latitude": 53.8000,
            "longitude": -1.5500,
            "event_id": "A-1",
            "sensor_type": "gps",
            "visible": "true",
        }
    )
    create_trackpoint(
        {
            "gull_id": gull_b["id"],
            "recorded_at": "2009-07-01T11:05:00Z",
            "latitude": 54.0000,
            "longitude": -1.2000,
            "event_id": "B-1",
            "sensor_type": "gps",
            "visible": "true",
        }
    )

    response = client.get("/api/v1/trackpoints", params={"gull_id": gull_a["id"]})
    if response.status_code == 404:
        response = client.get("/api/v1/trackpoints/", params={"gull_id": gull_a["id"]})

    assert response.status_code == 200, response.text
    data = response.json()

    assert len(data) >= 1
    ids = {item["id"] for item in data}
    assert tp_a["id"] in ids
    assert all(item["gull_id"] == gull_a["id"] for item in data)


def test_get_trackpoint_by_id(client, create_gull, create_trackpoint, gull_payload):
    gull = create_gull(gull_payload)
    created = create_trackpoint(
        {
            "gull_id": gull["id"],
            "recorded_at": "2009-07-01T10:05:00Z",
            "latitude": 53.8000,
            "longitude": -1.5500,
            "event_id": "TP-GET-1",
            "sensor_type": "gps",
            "visible": "true",
        }
    )

    response = client.get(f"/api/v1/trackpoints/{created['id']}")
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["id"] == created["id"]
    assert data["event_id"] == "TP-GET-1"


def test_get_trackpoint_unknown_id_returns_404(client):
    response = client.get("/api/v1/trackpoints/999999")
    assert response.status_code == 404, response.text


def test_get_trackpoint_invalid_path_type_returns_422(client):
    response = client.get("/api/v1/trackpoints/not-an-int")
    assert response.status_code == 422, response.text


def test_put_trackpoint(client, create_gull, create_trackpoint, gull_payload):
    gull = create_gull(gull_payload)
    created = create_trackpoint(
        {
            "gull_id": gull["id"],
            "recorded_at": "2009-07-01T10:05:00Z",
            "latitude": 53.8000,
            "longitude": -1.5500,
            "event_id": "TP-PUT-1",
            "sensor_type": "gps",
            "visible": "true",
        }
    )

    payload = {
        "gull_id": gull["id"],
        "recorded_at": "2009-07-01T10:15:00Z",
        "latitude": 53.8050,
        "longitude": -1.5450,
        "event_id": "TP-PUT-UPDATED",
        "sensor_type": "gps",
        "visible": "false",
    }

    response = client.put(f"/api/v1/trackpoints/{created['id']}", json=payload)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == created["id"]
    assert data["event_id"] == "TP-PUT-UPDATED"
    assert data["latitude"] == 53.8050
    assert data["visible"] == "false"


def test_patch_trackpoint(client, create_gull, create_trackpoint, gull_payload):
    gull = create_gull(gull_payload)
    created = create_trackpoint(
        {
            "gull_id": gull["id"],
            "recorded_at": "2009-07-01T10:05:00Z",
            "latitude": 53.8000,
            "longitude": -1.5500,
            "event_id": "TP-PATCH-1",
            "sensor_type": "gps",
            "visible": "true",
        }
    )

    patch_payload = {
        "visible": "false",
        "event_id": "TP-PATCH-UPDATED",
    }

    response = client.patch(f"/api/v1/trackpoints/{created['id']}", json=patch_payload)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == created["id"]
    assert data["visible"] == "false"
    assert data["event_id"] == "TP-PATCH-UPDATED"


def test_delete_trackpoint(client, create_gull, create_trackpoint, gull_payload):
    gull = create_gull(gull_payload)
    created = create_trackpoint(
        {
            "gull_id": gull["id"],
            "recorded_at": "2009-07-01T10:05:00Z",
            "latitude": 53.8000,
            "longitude": -1.5500,
            "event_id": "TP-DELETE-1",
            "sensor_type": "gps",
            "visible": "true",
        }
    )

    response = client.delete(f"/api/v1/trackpoints/{created['id']}")
    assert response.status_code == 204, response.text

    get_response = client.get(f"/api/v1/trackpoints/{created['id']}")
    assert get_response.status_code == 404, get_response.text


def test_delete_trackpoint_unknown_id_returns_404(client):
    response = client.delete("/api/v1/trackpoints/999999")
    assert response.status_code == 404, response.text


def test_trackpoint_validation_rejects_invalid_latitude(client, create_gull, gull_payload):
    gull = create_gull(gull_payload)

    invalid_payload = {
        "gull_id": gull["id"],
        "recorded_at": "2009-07-01T10:05:00Z",
        "latitude": 123.456,
        "longitude": -1.5500,
        "event_id": "BAD-LAT",
        "sensor_type": "gps",
        "visible": "true",
    }

    response = client.post("/api/v1/trackpoints", json=invalid_payload)
    if response.status_code == 404:
        response = client.post("/api/v1/trackpoints/", json=invalid_payload)

    assert response.status_code == 422, response.text
    assert "detail" in response.json()


def test_trackpoint_validation_rejects_invalid_longitude(client, create_gull, gull_payload):
    gull = create_gull(gull_payload)

    invalid_payload = {
        "gull_id": gull["id"],
        "recorded_at": "2009-07-01T10:05:00Z",
        "latitude": 53.8000,
        "longitude": -200.0,
        "event_id": "BAD-LON",
        "sensor_type": "gps",
        "visible": "true",
    }

    response = client.post("/api/v1/trackpoints", json=invalid_payload)
    if response.status_code == 404:
        response = client.post("/api/v1/trackpoints/", json=invalid_payload)

    assert response.status_code == 422, response.text
    assert "detail" in response.json()


def test_trackpoint_allows_nullable_sensor_type(client, create_gull, gull_payload):
    gull = create_gull(gull_payload)

    payload = {
        "gull_id": gull["id"],
        "recorded_at": "2009-07-01T10:05:00Z",
        "latitude": 53.8000,
        "longitude": -1.5500,
        "event_id": "NULL-SENSOR",
        "visible": "true",
    }

    response = client.post("/api/v1/trackpoints", json=payload)
    if response.status_code == 404:
        response = client.post("/api/v1/trackpoints/", json=payload)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["event_id"] == "NULL-SENSOR"
    assert data["sensor_type"] is None


def test_trackpoint_validation_rejects_missing_gull_id(client):
    invalid_payload = {
        "recorded_at": "2009-07-01T10:05:00Z",
        "latitude": 53.8000,
        "longitude": -1.5500,
        "event_id": "NO-GULL-ID",
        "sensor_type": "gps",
        "visible": "true",
    }

    response = client.post("/api/v1/trackpoints", json=invalid_payload)
    if response.status_code == 404:
        response = client.post("/api/v1/trackpoints/", json=invalid_payload)

    assert response.status_code == 422, response.text
    assert "detail" in response.json()


def test_get_trackpoint_weather_match(client, seeded_route):
    trackpoint_id = seeded_route["trackpoints"][0]["id"]

    response = client.get(f"/api/v1/trackpoints/{trackpoint_id}/weather")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["trackpoint_id"] == trackpoint_id
    assert "weather_id" in data
    assert "time_difference_minutes" in data
    assert "distance_km" in data
    assert "temperature_c" in data


def test_get_trackpoint_weather_match_unknown_id_returns_404(client):
    response = client.get("/api/v1/trackpoints/999999/weather")
    assert response.status_code == 404, response.text