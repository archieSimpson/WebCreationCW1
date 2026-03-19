from __future__ import annotations

import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.gull import Gull
from app.models.gull_trackpoint import GullTrackPoint
from app.models.weather import WeatherObservation


GULLS_CSV = PROJECT_ROOT / "data" / "Navigation experiments in lesser black-backed gulls (data from Wikelski et al. 2015).csv"
WEATHER_CSV = PROJECT_ROOT / "data" / "output_gulls_with_weather.csv"

COMMON_NAME = "Lesser Black-backed Gull"
WEATHER_SOURCE = "Prepared CSV import"
WEATHER_DATASET_NAME = "output_gulls_with_weather"
BATCH_SIZE = 5000


def clean_value(value):
    if pd.isna(value):
        return None
    return value


def parse_bool_to_string(value):
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value).strip()
    if not text:
        return None
    return text.lower()


def wind_speed_dir_to_uv(speed, direction_degrees):
    if pd.isna(speed) or pd.isna(direction_degrees):
        return None, None

    speed = float(speed)
    direction_degrees = float(direction_degrees)
    radians = math.radians(direction_degrees)

    u = -speed * math.sin(radians)
    v = -speed * math.cos(radians)
    return u, v


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    return pd.read_csv(path)


def import_gulls_and_trackpoints():
    df = read_csv(GULLS_CSV)

    required_columns = [
        "event-id",
        "timestamp",
        "location-long",
        "location-lat",
        "sensor-type",
        "individual-taxon-canonical-name",
        "individual-local-identifier",
        "study-name",
        "visible",
    ]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required gull CSV columns: {missing}")

    db = SessionLocal()
    try:
        print("Loading existing gulls...")
        existing_gulls = {
            g.tag_id: g.id
            for g in db.execute(select(Gull)).scalars().all()
        }

        unique_gulls_df = (
            df[
                [
                    "individual-local-identifier",
                    "individual-taxon-canonical-name",
                    "study-name",
                ]
            ]
            .drop_duplicates()
            .copy()
        )

        gull_rows = []
        for _, row in unique_gulls_df.iterrows():
            tag_id = str(row["individual-local-identifier"]).strip()
            if not tag_id or tag_id in existing_gulls:
                continue

            gull_rows.append(
                {
                    "tag_id": tag_id,
                    "species": str(row["individual-taxon-canonical-name"]).strip(),
                    "common_name": COMMON_NAME,
                    "study_name": clean_value(row["study-name"]),
                }
            )

        if gull_rows:
            print(f"Inserting {len(gull_rows)} gulls...")
            db.bulk_insert_mappings(Gull, gull_rows)
            db.commit()
        else:
            print("No new gulls to insert.")

        gull_lookup = {
            g.tag_id: g.id
            for g in db.execute(select(Gull)).scalars().all()
        }

        print("Loading existing trackpoint event_ids...")
        existing_event_ids = set(
            db.execute(
                select(GullTrackPoint.event_id).where(GullTrackPoint.event_id.is_not(None))
            ).scalars().all()
        )

        trackpoint_rows = []
        inserted_count = 0

        for _, row in df.iterrows():
            event_id = str(row["event-id"]).strip() if not pd.isna(row["event-id"]) else None
            if event_id and event_id in existing_event_ids:
                continue

            tag_id = str(row["individual-local-identifier"]).strip()
            gull_id = gull_lookup.get(tag_id)
            if gull_id is None:
                continue

            recorded_at = pd.to_datetime(row["timestamp"], utc=True).to_pydatetime()

            trackpoint_rows.append(
                {
                    "gull_id": gull_id,
                    "recorded_at": recorded_at,
                    "latitude": float(row["location-lat"]),
                    "longitude": float(row["location-long"]),
                    "event_id": event_id,
                    "sensor_type": clean_value(row["sensor-type"]),
                    "visible": parse_bool_to_string(row["visible"]),
                }
            )

            if event_id:
                existing_event_ids.add(event_id)

            if len(trackpoint_rows) >= BATCH_SIZE:
                db.bulk_insert_mappings(GullTrackPoint, trackpoint_rows)
                db.commit()
                inserted_count += len(trackpoint_rows)
                print(f"Inserted {inserted_count} trackpoints...")
                trackpoint_rows = []

        if trackpoint_rows:
            db.bulk_insert_mappings(GullTrackPoint, trackpoint_rows)
            db.commit()
            inserted_count += len(trackpoint_rows)

        print(f"Trackpoint import complete. Inserted {inserted_count} new trackpoints.")

    finally:
        db.close()


def import_weather():
    df = read_csv(WEATHER_CSV)

    required_columns = [
        "timestamp",
        "location-long",
        "location-lat",
        "temperature_2m",
        "precipitation",
        "wind_speed_10m",
        "wind_direction_10m",
        "surface_pressure",
    ]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required weather CSV columns: {missing}")

    db = SessionLocal()
    try:
        print("Loading existing weather keys...")
        existing_weather_keys = set(
            db.execute(
                select(
                    WeatherObservation.observed_at,
                    WeatherObservation.latitude,
                    WeatherObservation.longitude,
                )
            ).all()
        )

        weather_rows = []
        inserted_count = 0

        for _, row in df.iterrows():
            observed_at = pd.to_datetime(row["timestamp"], utc=True).to_pydatetime()
            latitude = float(row["location-lat"])
            longitude = float(row["location-long"])

            key = (observed_at, latitude, longitude)
            if key in existing_weather_keys:
                continue

            wind_u, wind_v = wind_speed_dir_to_uv(
                row["wind_speed_10m"],
                row["wind_direction_10m"],
            )

            weather_rows.append(
                {
                    "observed_at": observed_at,
                    "latitude": latitude,
                    "longitude": longitude,
                    "year": observed_at.year,
                    "temperature_c": None if pd.isna(row["temperature_2m"]) else float(row["temperature_2m"]),
                    "precipitation_mm": None if pd.isna(row["precipitation"]) else float(row["precipitation"]),
                    "wind_u": wind_u,
                    "wind_v": wind_v,
                    "surface_pressure": None if pd.isna(row["surface_pressure"]) else float(row["surface_pressure"]),
                    "source": WEATHER_SOURCE,
                    "dataset_name": WEATHER_DATASET_NAME,
                }
            )

            existing_weather_keys.add(key)

            if len(weather_rows) >= BATCH_SIZE:
                db.bulk_insert_mappings(WeatherObservation, weather_rows)
                db.commit()
                inserted_count += len(weather_rows)
                print(f"Inserted {inserted_count} weather observations...")
                weather_rows = []

        if weather_rows:
            db.bulk_insert_mappings(WeatherObservation, weather_rows)
            db.commit()
            inserted_count += len(weather_rows)

        print(f"Weather import complete. Inserted {inserted_count} new weather observations.")

    finally:
        db.close()


def main():
    print("Starting local CSV import...")
    import_gulls_and_trackpoints()
    import_weather()
    print("All imports finished successfully.")


if __name__ == "__main__":
    main()