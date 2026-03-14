from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GullTrackPoint(Base):
    __tablename__ = "gull_trackpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gull_id: Mapped[int] = mapped_column(
        ForeignKey("gulls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    event_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sensor_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    visible: Mapped[str | None] = mapped_column(String(30), nullable=True)

    gull = relationship("Gull", back_populates="trackpoints")

    __table_args__ = (
        Index("ix_gull_trackpoints_gull_recorded_at", "gull_id", "recorded_at"),
    )