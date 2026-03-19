from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.gull_trackpoint import GullTrackPoint
from app.schemas.analytics import TrackpointWeatherMatchRead
from app.services.weather_match import find_best_weather_match

from app.api.deps import get_db
from app.models.gull import Gull
from app.schemas.gull_trackpoint import (
    GullTrackPointCreate,
    GullTrackPointRead,
    GullTrackPointUpdate,
)

router = APIRouter()


@router.get("", response_model=list[GullTrackPointRead])
def list_gull_trackpoints(
    gull_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(GullTrackPoint)
    if gull_id is not None:
        stmt = stmt.where(GullTrackPoint.gull_id == gull_id)
    return db.execute(stmt.order_by(GullTrackPoint.recorded_at)).scalars().all()


@router.post("", response_model=GullTrackPointRead, status_code=status.HTTP_201_CREATED)
def create_gull_trackpoint(payload: GullTrackPointCreate, db: Session = Depends(get_db)):
    gull = db.get(Gull, payload.gull_id)
    if not gull:
        raise HTTPException(status_code=404, detail="Referenced gull not found.")

    trackpoint = GullTrackPoint(**payload.model_dump())
    db.add(trackpoint)
    db.commit()
    db.refresh(trackpoint)
    return trackpoint


@router.get("/{trackpoint_id}", response_model=GullTrackPointRead)
def get_gull_trackpoint(trackpoint_id: int, db: Session = Depends(get_db)):
    trackpoint = db.get(GullTrackPoint, trackpoint_id)
    if not trackpoint:
        raise HTTPException(status_code=404, detail="Gull trackpoint not found.")
    return trackpoint


@router.put("/{trackpoint_id}", response_model=GullTrackPointRead)
def update_gull_trackpoint_full(
    trackpoint_id: int,
    payload: GullTrackPointCreate,
    db: Session = Depends(get_db),
):
    trackpoint = db.get(GullTrackPoint, trackpoint_id)
    if not trackpoint:
        raise HTTPException(status_code=404, detail="Gull trackpoint not found.")

    gull = db.get(Gull, payload.gull_id)
    if not gull:
        raise HTTPException(status_code=404, detail="Referenced gull not found.")

    for key, value in payload.model_dump().items():
        setattr(trackpoint, key, value)

    db.commit()
    db.refresh(trackpoint)
    return trackpoint


@router.patch("/{trackpoint_id}", response_model=GullTrackPointRead)
def update_gull_trackpoint_partial(
    trackpoint_id: int,
    payload: GullTrackPointUpdate,
    db: Session = Depends(get_db),
):
    trackpoint = db.get(GullTrackPoint, trackpoint_id)
    if not trackpoint:
        raise HTTPException(status_code=404, detail="Gull trackpoint not found.")

    update_data = payload.model_dump(exclude_unset=True)

    if "gull_id" in update_data:
        gull = db.get(Gull, update_data["gull_id"])
        if not gull:
            raise HTTPException(status_code=404, detail="Referenced gull not found.")

    for key, value in update_data.items():
        setattr(trackpoint, key, value)

    db.commit()
    db.refresh(trackpoint)
    return trackpoint


@router.delete("/{trackpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gull_trackpoint(trackpoint_id: int, db: Session = Depends(get_db)):
    trackpoint = db.get(GullTrackPoint, trackpoint_id)
    if not trackpoint:
        raise HTTPException(status_code=404, detail="Gull trackpoint not found.")
    db.delete(trackpoint)
    db.commit()


@router.get(
    "/{trackpoint_id}/weather",
    response_model=TrackpointWeatherMatchRead,
    summary="Get the best matching weather observation for a trackpoint",
)
def get_trackpoint_weather(trackpoint_id: int, db: Session = Depends(get_db)):
    trackpoint = db.get(GullTrackPoint, trackpoint_id)
    if not trackpoint:
        raise HTTPException(status_code=404, detail="Trackpoint not found.")

    weather, distance_km, time_difference_minutes = find_best_weather_match(
        db,
        recorded_at=trackpoint.recorded_at,
        latitude=trackpoint.latitude,
        longitude=trackpoint.longitude,
        hours_window=3,
    )

    if not weather:
        raise HTTPException(
            status_code=404,
            detail="No matching weather observation found within the time window.",
        )

    return TrackpointWeatherMatchRead(
        trackpoint_id=trackpoint.id,
        gull_id=trackpoint.gull_id,
        weather_id=weather.id,
        trackpoint_recorded_at=trackpoint.recorded_at,
        weather_observed_at=weather.observed_at,
        time_difference_minutes=time_difference_minutes,
        distance_km=distance_km,
        match_method="nearest weather within ±3 hours by spatial distance",
        latitude=weather.latitude,
        longitude=weather.longitude,
        temperature_c=weather.temperature_c,
        precipitation_mm=weather.precipitation_mm,
        wind_u=weather.wind_u,
        wind_v=weather.wind_v,
        surface_pressure=weather.surface_pressure,
    )