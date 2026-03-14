from datetime import datetime

from pydantic import BaseModel, Field


class WeatherObservationBase(BaseModel):
    observed_at: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    year: int
    temperature_c: float | None = None
    precipitation_mm: float | None = None
    wind_u: float | None = None
    wind_v: float | None = None
    surface_pressure: float | None = None
    source: str | None = None
    dataset_name: str | None = None


class WeatherObservationCreate(WeatherObservationBase):
    pass


class WeatherObservationRead(WeatherObservationBase):
    id: int

    model_config = {"from_attributes": True}


class WeatherCoverageRead(BaseModel):
    available_years: list[int]
    total_records: int
    earliest_timestamp: datetime | None
    latest_timestamp: datetime | None