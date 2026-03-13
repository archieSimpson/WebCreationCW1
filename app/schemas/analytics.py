from datetime import datetime
from pydantic import BaseModel


class TrackpointWeatherMatchRead(BaseModel):
    trackpoint_id: int
    gull_id: int
    weather_id: int

    trackpoint_recorded_at: datetime
    weather_observed_at: datetime

    time_difference_minutes: float
    distance_km: float
    match_method: str

    latitude: float
    longitude: float

    temperature_c: float | None = None
    precipitation_mm: float | None = None
    wind_u: float | None = None
    wind_v: float | None = None
    surface_pressure: float | None = None

    model_config = {"from_attributes": True}


class GullMovementSummaryRead(BaseModel):
    gull_id: int
    tag_id: str
    species: str
    total_trackpoints: int

    first_recorded_at: datetime | None
    last_recorded_at: datetime | None
    duration_hours: float

    total_distance_km: float
    average_step_distance_km: float

    average_temperature_c: float | None
    average_precipitation_mm: float | None

    model_config = {"from_attributes": True}