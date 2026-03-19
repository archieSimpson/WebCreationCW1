# backend/tests/test_gulls_api.py
from __future__ import annotations


def test_create_gull(client, gull_payload):
    response = client.post("/api/v1/gulls/", json=gull_payload)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["id"] > 0
    assert data["tag_id"] == gull_payload["tag_id"]
    assert data["species"] == gull_payload["species"]
    assert data["common_name"] == gull_payload["common_name"]
    assert data["study_name"] == gull_payload["study_name"]


def test_list_gulls_returns_created_items(client, create_gull, gull_payload, second_gull_payload):
    gull_a = create_gull(gull_payload)
    gull_b = create_gull(second_gull_payload)

    response = client.get("/api/v1/gulls/")
    assert response.status_code == 200, response.text

    data = response.json()
    ids = {item["id"] for item in data}
    assert gull_a["id"] in ids
    assert gull_b["id"] in ids


def test_list_gulls_can_filter_by_species(client, create_gull, gull_payload, second_gull_payload):
    created_a = create_gull(gull_payload)
    create_gull(second_gull_payload)

    response = client.get("/api/v1/gulls/", params={"species": created_a["species"]})
    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) >= 1
    assert all(item["species"] == created_a["species"] for item in data)


def test_get_single_gull(client, create_gull, gull_payload):
    created = create_gull(gull_payload)

    response = client.get(f"/api/v1/gulls/{created['id']}")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == created["id"]
    assert data["tag_id"] == gull_payload["tag_id"]


def test_put_updates_gull_fully(client, create_gull, gull_payload):
    created = create_gull(gull_payload)

    update_payload = {
        "tag_id": "GULL-A-UPDATED",
        "species": "Updated species",
        "common_name": "Updated common name",
        "study_name": "Updated study",
    }

    response = client.put(f"/api/v1/gulls/{created['id']}", json=update_payload)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == created["id"]
    assert data["tag_id"] == "GULL-A-UPDATED"
    assert data["species"] == "Updated species"
    assert data["common_name"] == "Updated common name"
    assert data["study_name"] == "Updated study"


def test_patch_updates_gull_partially(client, create_gull, gull_payload):
    created = create_gull(gull_payload)

    patch_payload = {
        "common_name": "Patched Gull Name",
    }

    response = client.patch(f"/api/v1/gulls/{created['id']}", json=patch_payload)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == created["id"]
    assert data["common_name"] == "Patched Gull Name"
    assert data["tag_id"] == gull_payload["tag_id"]
    assert data["species"] == gull_payload["species"]


def test_delete_gull(client, create_gull, gull_payload):
    created = create_gull(gull_payload)

    delete_response = client.delete(f"/api/v1/gulls/{created['id']}")
    assert delete_response.status_code == 204, delete_response.text

    get_response = client.get(f"/api/v1/gulls/{created['id']}")
    assert get_response.status_code in {404, 422}, get_response.text


def test_create_gull_allows_nullable_study_name(client):
    payload = {
        "tag_id": "BAD-GULL-1",
        "species": "Larus fuscus",
        "common_name": "Lesser Black-backed Gull",
    }

    response = client.post("/api/v1/gulls/", json=payload)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["tag_id"] == payload["tag_id"]
    assert data["study_name"] is None


def test_gull_id_validation_error_for_non_integer_path(client):
    response = client.get("/api/v1/gulls/not-an-int")
    assert response.status_code == 422, response.text