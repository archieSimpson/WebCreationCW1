from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Gull Migration patterns and corosponding weather data COMP3011 coursework."
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_V1_STR)