from fastapi import APIRouter
from app.api.v1.endpoints import gull_trackpoints, gulls, weather

api_router = APIRouter()
api_router.include_router(gulls.router, prefix="/gulls", tags=["gulls"])
api_router.include_router(gull_trackpoints.router, prefix="/trackpoints", tags=["trackpoints"])
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])