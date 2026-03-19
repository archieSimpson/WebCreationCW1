from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Gull(Base):
    __tablename__ = "gulls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tag_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    species: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    common_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    study_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    trackpoints = relationship(
        "GullTrackPoint",
        back_populates="gull",
        cascade="all, delete-orphan",
    )