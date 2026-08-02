from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kall.config import get_settings
from kall.db import create_db_and_tables
from kall.router_registry import register_api_routers

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_tables and settings.app_env in {"development", "test"}:
        create_db_and_tables()
    yield


app = FastAPI(
    title="Kall API",
    version="0.8.1",
    description="Career identity, scheduled opportunity discovery, growth, and review-before-submit applications",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_api_routers(app)
