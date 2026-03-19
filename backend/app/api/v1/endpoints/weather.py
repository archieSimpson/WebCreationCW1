from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.weather import WeatherObservation
from app.schemas.weather import (
    WeatherCoverageRead,
    WeatherObservationCreate,
    WeatherObservationRead,
)

router = APIRouter()


class WeatherObservationUpdate(BaseModel):
    observed_at: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    year: int
    temperature_c: float | None = None
    precipitation_mm: float | None = None
    wind_u: float | None = None
    wind_v: float | None = None
    surface_pressure: float | None = None
    source: str | None = None
    dataset_name: str | None = None


class WeatherObservationPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observed_at: datetime | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    year: int | None = None
    temperature_c: float | None = None
    precipitation_mm: float | None = None
    wind_u: float | None = None
    wind_v: float | None = None
    surface_pressure: float | None = None
    source: str | None = None
    dataset_name: str | None = None


@router.get("", response_model=list[WeatherObservationRead])
def list_weather(
    year: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(WeatherObservation)
    if year is not None:
        stmt = stmt.where(WeatherObservation.year == year)
    return db.execute(stmt.order_by(WeatherObservation.observed_at)).scalars().all()


@router.post("", response_model=WeatherObservationRead, status_code=status.HTTP_201_CREATED)
def create_weather(payload: WeatherObservationCreate, db: Session = Depends(get_db)):
    weather = WeatherObservation(**payload.model_dump())
    db.add(weather)
    db.commit()
    db.refresh(weather)
    return weather


@router.get("/{weather_id}", response_model=WeatherObservationRead)
def get_weather(weather_id: int, db: Session = Depends(get_db)):
    weather = db.get(WeatherObservation, weather_id)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather observation not found.")
    return weather


@router.put("/{weather_id}", response_model=WeatherObservationRead)
def update_weather(
    weather_id: int,
    payload: WeatherObservationUpdate,
    db: Session = Depends(get_db),
):
    weather = db.get(WeatherObservation, weather_id)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather observation not found.")

    for field, value in payload.model_dump().items():
        setattr(weather, field, value)

    db.add(weather)
    db.commit()
    db.refresh(weather)
    return weather


@router.patch("/{weather_id}", response_model=WeatherObservationRead)
def patch_weather(
    weather_id: int,
    payload: WeatherObservationPatch,
    db: Session = Depends(get_db),
):
    weather = db.get(WeatherObservation, weather_id)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather observation not found.")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(weather, field, value)

    db.add(weather)
    db.commit()
    db.refresh(weather)
    return weather


@router.delete("/{weather_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weather(weather_id: int, db: Session = Depends(get_db)):
    weather = db.get(WeatherObservation, weather_id)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather observation not found.")
    db.delete(weather)
    db.commit()


@router.get("/coverage/summary", response_model=WeatherCoverageRead)
def weather_coverage(db: Session = Depends(get_db)):
    years = db.execute(
        select(WeatherObservation.year).distinct().order_by(WeatherObservation.year)
    ).scalars().all()

    total_records = db.execute(
        select(func.count(WeatherObservation.id))
    ).scalar_one()

    earliest = db.execute(
        select(func.min(WeatherObservation.observed_at))
    ).scalar_one()

    latest = db.execute(
        select(func.max(WeatherObservation.observed_at))
    ).scalar_one()

    return {
        "available_years": years,
        "total_records": total_records,
        "earliest_timestamp": earliest,
        "latest_timestamp": latest,
    }