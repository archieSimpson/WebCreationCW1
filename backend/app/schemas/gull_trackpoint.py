from datetime import datetime

from pydantic import BaseModel, Field


class TrackpointWithWeatherRead(BaseModel):
    id: int
    gull_id: int
    recorded_at: datetime
    latitude: float
    longitude: float
    event_id: str | None = None
    sensor_type: str | None = None
    visible: str | None = None

    temperature_c: float | None = None
    precipitation_mm: float | None = None
    wind_u: float | None = None
    wind_v: float | None = None
    surface_pressure: float | None = None
    weather_id: int | None = None
    weather_observed_at: datetime | None = None

    model_config = {"from_attributes": True}


class GullTrackPointBase(BaseModel):
    gull_id: int
    recorded_at: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    event_id: str | None = Field(default=None, max_length=100)
    sensor_type: str | None = Field(default=None, max_length=100)
    visible: str | None = Field(default=None, max_length=30)


class GullTrackPointCreate(GullTrackPointBase):
    pass


class GullTrackPointUpdate(BaseModel):
    gull_id: int | None = None
    recorded_at: datetime | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    event_id: str | None = Field(default=None, max_length=100)
    sensor_type: str | None = Field(default=None, max_length=100)
    visible: str | None = Field(default=None, max_length=30)


class GullTrackPointRead(GullTrackPointBase):
    id: int

    model_config = {"from_attributes": True}