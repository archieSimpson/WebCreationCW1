from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    precipitation_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_u: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_v: Mapped[float | None] = mapped_column(Float, nullable=True)
    surface_pressure: Mapped[float | None] = mapped_column(Float, nullable=True)

    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dataset_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        Index("ix_weather_observed_at_lat_lon", "observed_at", "latitude", "longitude"),
    )