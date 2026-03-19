from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.weather import WeatherObservation
from app.utils.geo import haversine_km


def find_best_weather_match(
    db: Session,
    *,
    recorded_at,
    latitude: float,
    longitude: float,
    hours_window: int = 3,
):
    start_time = recorded_at - timedelta(hours=hours_window)
    end_time = recorded_at + timedelta(hours=hours_window)

    stmt = select(WeatherObservation).where(
        WeatherObservation.observed_at >= start_time,
        WeatherObservation.observed_at <= end_time,
        WeatherObservation.latitude >= latitude - 2,
        WeatherObservation.latitude <= latitude + 2,
        WeatherObservation.longitude >= longitude - 2,
        WeatherObservation.longitude <= longitude + 2,
    )

    candidates = db.execute(stmt).scalars().all()
    if not candidates:
        return None, None, None

    best_weather = None
    best_distance = None
    best_time_diff_minutes = None

    for weather in candidates:
        distance_km = haversine_km(
            latitude,
            longitude,
            weather.latitude,
            weather.longitude,
        )
        time_diff_minutes = abs(
            (weather.observed_at - recorded_at).total_seconds()
        ) / 60.0

        if best_weather is None or (distance_km, time_diff_minutes) < (
            best_distance,
            best_time_diff_minutes,
        ):
            best_weather = weather
            best_distance = distance_km
            best_time_diff_minutes = time_diff_minutes

    return best_weather, best_distance, best_time_diff_minutes