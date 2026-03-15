# backend/tests/conftest.py
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend/ is on sys.path so "import app.main" works reliably
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

TEST_DATABASE_URL = "sqlite:///./test_gull_tracker.db"


def _import_first(paths: list[str]):
    errors: list[str] = []

    for path in paths:
        module_name, attr_name = path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_name)
            return getattr(module, attr_name)
        except Exception as exc:
            errors.append(f"{path} -> {type(exc).__name__}: {exc}")

    joined = "\n".join(errors)
    raise RuntimeError(
        "Could not import any of the requested paths.\n"
        f"Tried:\n{joined}"
    )


# FastAPI app
app = _import_first(
    [
        "app.main.app",
    ]
)

# DB dependency override target
get_db = _import_first(
    [
        "app.api.deps.get_db",
    ]
)

# Base metadata import
Base = _import_first(
    [
        "app.db.base.Base",
        "app.db.base_class.Base",
        "app.db.session.Base",
    ]
)

# Import models so tables are registered on Base.metadata
for model_module in [
    "app.models.gull",
    "app.models.gull_trackpoint",
    "app.models.weather",
    "app.models.user",
]:
    try:
        importlib.import_module(model_module)
    except Exception:
        pass


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    app.dependency_overrides[get_db] = override_get_db
    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    def _override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override

    with TestClient(app) as c:
        yield c

    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def gull_payload() -> dict:
    return {
        "tag_id": "GULL-A-001",
        "species": "Larus fuscus",
        "common_name": "Lesser Black-backed Gull",
        "study_name": "COMP3011 Testing Study",
    }


@pytest.fixture()
def second_gull_payload() -> dict:
    return {
        "tag_id": "GULL-B-001",
        "species": "Larus argentatus",
        "common_name": "Herring Gull",
        "study_name": "COMP3011 Testing Study",
    }


@pytest.fixture()
def weather_payload_1() -> dict:
    return {
        "observed_at": "2009-07-01T10:00:00Z",
        "latitude": 53.8000,
        "longitude": -1.5500,
        "year": 2009,
        "temperature_c": 18.5,
        "precipitation_mm": 0.2,
        "wind_u": 1.5,
        "wind_v": -0.5,
        "surface_pressure": 1012.3,
        "source": "test-seed",
        "dataset_name": "unit-test-weather",
    }


@pytest.fixture()
def weather_payload_2() -> dict:
    return {
        "observed_at": "2009-07-01T11:00:00Z",
        "latitude": 53.8100,
        "longitude": -1.5400,
        "year": 2009,
        "temperature_c": 19.0,
        "precipitation_mm": 0.0,
        "wind_u": 2.0,
        "wind_v": -0.2,
        "surface_pressure": 1011.8,
        "source": "test-seed",
        "dataset_name": "unit-test-weather",
    }


@pytest.fixture()
def weather_payload_3() -> dict:
    return {
        "observed_at": "2010-07-01T09:00:00Z",
        "latitude": 54.0000,
        "longitude": -1.2000,
        "year": 2010,
        "temperature_c": 15.1,
        "precipitation_mm": 1.1,
        "wind_u": -1.0,
        "wind_v": 0.8,
        "surface_pressure": 1008.0,
        "source": "test-seed",
        "dataset_name": "unit-test-weather",
    }


@pytest.fixture()
def create_gull(client):
    def _create(payload: dict) -> dict:
        response = client.post("/api/v1/gulls/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _create


@pytest.fixture()
def create_weather(client):
    def _create(payload: dict) -> dict:
        response = client.post("/api/v1/weather", json=payload)
        if response.status_code == 404:
            response = client.post("/api/v1/weather/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _create


@pytest.fixture()
def create_trackpoint(client):
    def _create(payload: dict) -> dict:
        response = client.post("/api/v1/trackpoints", json=payload)
        if response.status_code == 404:
            response = client.post("/api/v1/trackpoints/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _create


@pytest.fixture()
def seeded_route(client, create_gull, create_trackpoint, create_weather, gull_payload):
    gull = create_gull(gull_payload)

    weather_1 = create_weather(
        {
            "observed_at": "2009-07-01T10:00:00Z",
            "latitude": 53.8000,
            "longitude": -1.5500,
            "year": 2009,
            "temperature_c": 18.5,
            "precipitation_mm": 0.2,
            "wind_u": 1.5,
            "wind_v": -0.5,
            "surface_pressure": 1012.3,
            "source": "test-seed",
            "dataset_name": "unit-test-weather",
        }
    )
    weather_2 = create_weather(
        {
            "observed_at": "2009-07-01T11:00:00Z",
            "latitude": 53.8100,
            "longitude": -1.5400,
            "year": 2009,
            "temperature_c": 19.0,
            "precipitation_mm": 0.0,
            "wind_u": 2.0,
            "wind_v": -0.2,
            "surface_pressure": 1011.8,
            "source": "test-seed",
            "dataset_name": "unit-test-weather",
        }
    )

    tp1 = create_trackpoint(
        {
            "gull_id": gull["id"],
            "recorded_at": "2009-07-01T10:05:00Z",
            "latitude": 53.8000,
            "longitude": -1.5500,
            "event_id": "EVT-1",
            "sensor_type": "gps",
            "visible": "true",
        }
    )
    tp2 = create_trackpoint(
        {
            "gull_id": gull["id"],
            "recorded_at": "2009-07-01T10:35:00Z",
            "latitude": 53.8050,
            "longitude": -1.5450,
            "event_id": "EVT-2",
            "sensor_type": "gps",
            "visible": "true",
        }
    )
    tp3 = create_trackpoint(
        {
            "gull_id": gull["id"],
            "recorded_at": "2009-07-01T11:05:00Z",
            "latitude": 53.8100,
            "longitude": -1.5400,
            "event_id": "EVT-3",
            "sensor_type": "gps",
            "visible": "true",
        }
    )

    return {
        "gull": gull,
        "trackpoints": [tp1, tp2, tp3],
        "weather": [weather_1, weather_2],
    }