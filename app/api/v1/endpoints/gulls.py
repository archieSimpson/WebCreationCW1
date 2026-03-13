from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.gull import Gull
from app.schemas.gull import GullCreate, GullRead, GullUpdate

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