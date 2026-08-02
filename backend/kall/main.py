from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kall.api import router
from kall.config import get_settings
from kall.db import create_db_and_tables
from kall.profile_api import router as profile_router

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_tables and settings.app_env in {"development", "test"}:
        create_db_and_tables()
    yield


app = FastAPI(
    title="Kall API",
    version="0.4.0",
    description="Career identity, onboarding, professional profiles, job discovery, and review-before-submit applications",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")
app.include_router(profile_router, prefix="/api")
