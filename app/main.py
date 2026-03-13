from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Animal tracking and weather context API for COMP3011 coursework."
)

app.include_router(api_router, prefix=settings.API_V1_STR)