from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.gull import Gull  # noqa: E402,F401
from app.models.gull_trackpoint import GullTrackPoint  # noqa: E402,F401
from app.models.weather import WeatherObservation  # noqa: E402,F401