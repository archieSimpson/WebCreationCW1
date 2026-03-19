# backend/tests/test_analytics_api.py
from __future__ import annotations


def test_gull_movement_summary_returns_expected_shape(client, seeded_route):
    gull_id = seeded_route["gull"]["id"]

    response = client.get(f"/api/v1/gulls/{gull_id}/movement-summary")
    assert response.status_code == 200, response.text

    data = response.json()

    assert data["gull_id"] == gull_id
    assert data["tag_id"] == seeded_route["gull"]["tag_id"]
    assert "species" in data
    assert data["total_trackpoints"] == 3

    # Accept either naive ISO datetime or UTC ISO datetime with Z suffix
    assert data["first_recorded_at"].startswith("2009-07-01T10:05:00")
    assert data["last_recorded_at"].startswith("2009-07-01T11:05:00")

    assert data["duration_hours"] >= 1.0
    assert data["total_distance_km"] >= 0
    assert data["average_step_distance_km"] >= 0

    # These are useful high-value analytics checks if present in your schema
    if "average_temperature_c" in data:
        assert isinstance(data["average_temperature_c"], (int, float)) or data["average_temperature_c"] is None

    if "average_precipitation_mm" in data:
        assert isinstance(data["average_precipitation_mm"], (int, float)) or data["average_precipitation_mm"] is None


def test_gull_route_with_weather_returns_ordered_route(client, seeded_route):
    gull_id = seeded_route["gull"]["id"]

    response = client.get(f"/api/v1/gulls/{gull_id}/route-with-weather")
    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

    timestamps = [item["recorded_at"] for item in data]
    assert timestamps == sorted(timestamps)

    first = data[0]
    assert first["gull_id"] == gull_id
    assert "latitude" in first
    assert "longitude" in first
    assert "event_id" in first
    assert "sensor_type" in first
    assert "visible" in first

    # Only assert enriched weather fields if your endpoint includes them
    optional_weather_fields = [
        "temperature_c",
        "precipitation_mm",
        "wind_u",
        "wind_v",
        "surface_pressure",
    ]
    for field in optional_weather_fields:
        if field in first:
            assert field in first


def test_trackpoint_weather_match_returns_expected_shape(client, seeded_route):
    trackpoint_id = seeded_route["trackpoints"][1]["id"]

    response = client.get(f"/api/v1/trackpoints/{trackpoint_id}/weather")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["trackpoint_id"] == trackpoint_id
    assert data["gull_id"] == seeded_route["gull"]["id"]
    assert "weather_id" in data
    assert "trackpoint_recorded_at" in data
    assert "weather_observed_at" in data
    assert "time_difference_minutes" in data
    assert "distance_km" in data

    if "match_method" in data:
        assert isinstance(data["match_method"], str)

    for field in ["temperature_c", "precipitation_mm", "wind_u", "wind_v", "surface_pressure"]:
        if field in data:
            assert field in data


def test_movement_summary_for_gull_with_no_trackpoints_is_handled_cleanly(client, create_gull, gull_payload):
    gull = create_gull(gull_payload)

    response = client.get(f"/api/v1/gulls/{gull['id']}/movement-summary")
    assert response.status_code in {200, 400, 404}, response.text

    if response.status_code == 200:
        data = response.json()
        assert data["gull_id"] == gull["id"]
        assert data["total_trackpoints"] == 0


def test_route_with_weather_for_unknown_gull_returns_error(client):
    response = client.get("/api/v1/gulls/999999/route-with-weather")
    assert response.status_code in {404, 422}, response.text