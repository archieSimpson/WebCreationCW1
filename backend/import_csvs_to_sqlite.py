from __future__ import annotations

import math
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.gull import Gull
from app.models.gull_trackpoint import GullTrackPoint
from app.models.weather import WeatherObservation

DATABASE_URL = os.getenv("DATABASE_URL")

TRACKPOINTS_CSV = Path("./data/Navigation experiments in lesser black-backed gulls (data from Wikelski et al. 2015).csv")
WEATHER_CSV = Path("./data/output_gulls_with_weather.csv")

BATCH_SIZE = 2000


def require_database_url() -> str:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set.")
    return DATABASE_URL


def chunked(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def clean_str(value) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def clean_bool_string(value) -> str | None:
    if pd.isna(value):
        return None
    return str(value)


def to_utc_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


def wind_speed_dir_to_uv(speed, direction_degrees) -> tuple[float | None, float | None]:
    if pd.isna(speed) or pd.isna(direction_degrees):
        return None, None

    try:
        speed = float(speed)
        direction_degrees = float(direction_degrees)
    except (TypeError, ValueError):
        return None, None

    theta = math.radians(direction_degrees)
    u = -speed * math.sin(theta)
    v = -speed * math.cos(theta)
    return u, v


def main() -> None:
    db_url = require_database_url()

    if not TRACKPOINTS_CSV.exists():
        raise FileNotFoundError(f"Trackpoints CSV not found: {TRACKPOINTS_CSV}")

    if not WEATHER_CSV.exists():
        raise FileNotFoundError(f"Weather CSV not found: {WEATHER_CSV}")

    print(f"Using database: {db_url}")
    print(f"Trackpoints source: {TRACKPOINTS_CSV}")
    print(f"Weather source: {WEATHER_CSV}")

    engine = create_engine(db_url, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    with SessionLocal() as db:
        has_gulls = db.execute(select(Gull.id)).first()
        has_trackpoints = db.execute(select(GullTrackPoint.id)).first()
        has_weather = db.execute(select(WeatherObservation.id)).first()

        if has_gulls or has_trackpoints or has_weather:
            raise RuntimeError(
                "Target database is not empty. Delete local_gull_tracker.db and rerun."
            )

        print("Reading trackpoints CSV...")
        tp_df = pd.read_csv(TRACKPOINTS_CSV, low_memory=False)

        required_tp_cols = {
            "event-id",
            "visible",
            "timestamp",
            "location-long",
            "location-lat",
            "sensor-type",
            "individual-taxon-canonical-name",
            "tag-local-identifier",
            "study-name",
        }
        missing_tp = required_tp_cols - set(tp_df.columns)
        if missing_tp:
            raise ValueError(f"Missing required trackpoints columns: {sorted(missing_tp)}")

        tp_df["timestamp"] = to_utc_datetime(tp_df["timestamp"])
        tp_df = tp_df.dropna(
            subset=["timestamp", "location-lat", "location-long", "tag-local-identifier"]
        ).copy()

        print("Creating gull records...")
        gull_df = tp_df[
            ["tag-local-identifier", "individual-taxon-canonical-name", "study-name"]
        ].drop_duplicates().copy()

        tag_to_gull_id: dict[str, int] = {}

        gull_count = 0
        for _, row in gull_df.iterrows():
            tag_id = str(row["tag-local-identifier"]).strip()
            species = clean_str(row["individual-taxon-canonical-name"]) or "Unknown species"
            study_name = clean_str(row["study-name"])

            gull = Gull(
                tag_id=tag_id,
                species=species,
                common_name=None,
                study_name=study_name,
            )
            db.add(gull)
            db.flush()
            tag_to_gull_id[tag_id] = gull.id
            gull_count += 1

        db.commit()
        print(f"Inserted {gull_count} gulls.")

        print("Creating trackpoint records...")
        trackpoint_rows: list[GullTrackPoint] = []

        for _, row in tp_df.iterrows():
            tag_id = str(row["tag-local-identifier"]).strip()
            gull_id = tag_to_gull_id[tag_id]

            trackpoint_rows.append(
                GullTrackPoint(
                    gull_id=gull_id,
                    recorded_at=row["timestamp"].to_pydatetime(),
                    latitude=float(row["location-lat"]),
                    longitude=float(row["location-long"]),
                    event_id=clean_str(row.get("event-id")),
                    sensor_type=clean_str(row.get("sensor-type")),
                    visible=clean_bool_string(row.get("visible")),
                )
            )

        inserted_trackpoints = 0
        for batch in chunked(trackpoint_rows, BATCH_SIZE):
            db.add_all(batch)
            db.commit()
            inserted_trackpoints += len(batch)
            print(f"Inserted {inserted_trackpoints} trackpoints...")

        print(f"Inserted {inserted_trackpoints} trackpoints total.")

        print("Reading weather CSV...")
        weather_df = pd.read_csv(WEATHER_CSV, low_memory=False)

        required_weather_cols = {
            "timestamp",
            "location-long",
            "location-lat",
            "temperature_2m",
            "precipitation",
            "wind_speed_10m",
            "wind_direction_10m",
            "surface_pressure",
        }
        missing_weather = required_weather_cols - set(weather_df.columns)
        if missing_weather:
            raise ValueError(f"Missing required weather columns: {sorted(missing_weather)}")

        weather_df["timestamp"] = to_utc_datetime(weather_df["timestamp"])
        weather_df = weather_df.dropna(
            subset=["timestamp", "location-lat", "location-long"]
        ).copy()

        weather_df = weather_df.drop_duplicates(
            subset=["timestamp", "location-lat", "location-long"]
        ).copy()

        print("Creating weather observation records...")
        weather_rows: list[WeatherObservation] = []

        for _, row in weather_df.iterrows():
            observed_at = row["timestamp"].to_pydatetime()
            wind_u, wind_v = wind_speed_dir_to_uv(
                row.get("wind_speed_10m"),
                row.get("wind_direction_10m"),
            )

            weather_rows.append(
                WeatherObservation(
                    observed_at=observed_at,
                    latitude=float(row["location-lat"]),
                    longitude=float(row["location-long"]),
                    year=int(observed_at.year),
                    temperature_c=None if pd.isna(row.get("temperature_2m")) else float(row["temperature_2m"]),
                    precipitation_mm=None if pd.isna(row.get("precipitation")) else float(row["precipitation"]),
                    wind_u=wind_u,
                    wind_v=wind_v,
                    surface_pressure=None if pd.isna(row.get("surface_pressure")) else float(row["surface_pressure"]),
                    source="Open-Meteo Archive API",
                    dataset_name="output_gulls_with_weather.csv",
                )
            )

        inserted_weather = 0
        for batch in chunked(weather_rows, BATCH_SIZE):
            db.add_all(batch)
            db.commit()
            inserted_weather += len(batch)
            print(f"Inserted {inserted_weather} weather observations...")

        print(f"Inserted {inserted_weather} weather observations total.")

        final_gulls = len(db.execute(select(Gull)).scalars().all())
        final_trackpoints = len(db.execute(select(GullTrackPoint)).scalars().all())
        final_weather = len(db.execute(select(WeatherObservation)).scalars().all())

        print("Import complete.")
        print(f"Gulls: {final_gulls}")
        print(f"Trackpoints: {final_trackpoints}")
        print(f"Weather observations: {final_weather}")


if __name__ == "__main__":
    main()