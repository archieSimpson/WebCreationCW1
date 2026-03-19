from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.gull import Gull
from app.models.gull_trackpoint import GullTrackPoint
from app.schemas.analytics import GullMovementSummaryRead
from app.schemas.gull import GullCreate, GullRead, GullUpdate
from app.services.weather_match import find_best_weather_match
from app.utils.geo import haversine_km
router = APIRouter()


@router.get("/", response_model=list[GullRead])
def list_gulls(
    species: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Gull)
    if species:
        stmt = stmt.where(Gull.species == species)
    return db.execute(stmt.order_by(Gull.id)).scalars().all()


@router.post("/", response_model=GullRead, status_code=status.HTTP_201_CREATED)
def create_gull(payload: GullCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(Gull).where(Gull.tag_id == payload.tag_id)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Gull with this tag_id already exists.",
        )

    gull = Gull(**payload.model_dump())
    db.add(gull)
    db.commit()
    db.refresh(gull)
    return gull


@router.get("/{gull_id}", response_model=GullRead)
def get_gull(gull_id: int, db: Session = Depends(get_db)):
    gull = db.get(Gull, gull_id)
    if not gull:
        raise HTTPException(status_code=404, detail="Gull not found.")
    return gull


@router.get(
    "/{gull_id}/movement-summary",
    response_model=GullMovementSummaryRead,
    summary="Get a movement summary for a gull",
)
def get_gull_movement_summary(gull_id: int, db: Session = Depends(get_db)):
    gull = db.get(Gull, gull_id)
    if not gull:
        raise HTTPException(status_code=404, detail="Gull not found.")

    stmt = (
        select(GullTrackPoint)
        .where(GullTrackPoint.gull_id == gull_id)
        .order_by(GullTrackPoint.recorded_at)
    )

    trackpoints = db.execute(stmt).scalars().all()

    if not trackpoints:
        return GullMovementSummaryRead(
            gull_id=gull.id,
            tag_id=gull.tag_id,
            species=gull.species,
            total_trackpoints=0,
            first_recorded_at=None,
            last_recorded_at=None,
            duration_hours=0.0,
            total_distance_km=0.0,
            average_step_distance_km=0.0,
            average_temperature_c=None,
            average_precipitation_mm=None,
        )

    total_distance_km = 0.0

    for i in range(1, len(trackpoints)):
        prev_tp = trackpoints[i - 1]
        curr_tp = trackpoints[i]

        total_distance_km += haversine_km(
            prev_tp.latitude,
            prev_tp.longitude,
            curr_tp.latitude,
            curr_tp.longitude,
        )

    first_recorded_at = trackpoints[0].recorded_at
    last_recorded_at = trackpoints[-1].recorded_at
    total_trackpoints = len(trackpoints)

    duration_hours = (
        (last_recorded_at - first_recorded_at).total_seconds() / 3600
        if total_trackpoints > 1
        else 0
    )

    average_step_distance_km = (
        total_distance_km / (total_trackpoints - 1)
        if total_trackpoints > 1
        else 0
    )

    matched_temperatures = []
    matched_precipitation = []

    for tp in trackpoints:
        weather, _, _ = find_best_weather_match(
            db,
            recorded_at=tp.recorded_at,
            latitude=tp.latitude,
            longitude=tp.longitude,
        )

        if weather:
            if weather.temperature_c is not None:
                matched_temperatures.append(weather.temperature_c)

            if weather.precipitation_mm is not None:
                matched_precipitation.append(weather.precipitation_mm)

    avg_temp = (
        sum(matched_temperatures) / len(matched_temperatures)
        if matched_temperatures
        else None
    )

    avg_precip = (
        sum(matched_precipitation) / len(matched_precipitation)
        if matched_precipitation
        else None
    )

    return GullMovementSummaryRead(
        gull_id=gull.id,
        tag_id=gull.tag_id,
        species=gull.species,
        total_trackpoints=total_trackpoints,
        first_recorded_at=first_recorded_at,
        last_recorded_at=last_recorded_at,
        duration_hours=duration_hours,
        total_distance_km=total_distance_km,
        average_step_distance_km=average_step_distance_km,
        average_temperature_c=avg_temp,
        average_precipitation_mm=avg_precip,
    )

@router.put("/{gull_id}", response_model=GullRead)
def update_gull_full(gull_id: int, payload: GullCreate, db: Session = Depends(get_db)):
    gull = db.get(Gull, gull_id)
    if not gull:
        raise HTTPException(status_code=404, detail="Gull not found.")

    existing = db.execute(
        select(Gull).where(Gull.tag_id == payload.tag_id, Gull.id != gull_id)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Another gull with this tag_id already exists.",
        )

    for key, value in payload.model_dump().items():
        setattr(gull, key, value)

    db.commit()
    db.refresh(gull)
    return gull


@router.patch("/{gull_id}", response_model=GullRead)
def update_gull_partial(gull_id: int, payload: GullUpdate, db: Session = Depends(get_db)):
    gull = db.get(Gull, gull_id)
    if not gull:
        raise HTTPException(status_code=404, detail="Gull not found.")

    update_data = payload.model_dump(exclude_unset=True)

    if "tag_id" in update_data:
        existing = db.execute(
            select(Gull).where(Gull.tag_id == update_data["tag_id"], Gull.id != gull_id)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Another gull with this tag_id already exists.",
            )

    for key, value in update_data.items():
        setattr(gull, key, value)

    db.commit()
    db.refresh(gull)
    return gull


@router.delete("/{gull_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gull(gull_id: int, db: Session = Depends(get_db)):
    gull = db.get(Gull, gull_id)
    if not gull:
        raise HTTPException(status_code=404, detail="Gull not found.")

    db.delete(gull)
    db.commit()
    return None