from contextlib import asynccontextmanager
from fastapi import FastAPI
from kall.api import router
from kall.db import create_db_and_tables
@asynccontextmanager
async def lifespan(_:FastAPI):
    create_db_and_tables();yield
app=FastAPI(title='Kall API',version='0.1.0',description='Identity, professional profiles, Resume Studio, and review-before-submit applications',lifespan=lifespan)
app.include_router(router,prefix='/api')
