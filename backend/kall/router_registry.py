from fastapi import FastAPI

from kall.api import router
from kall.api_application_review import router as application_review_router
from kall.api_applications import router as applications_router
from kall.api_brief import router as brief_router
from kall.api_career_profiles import router as career_profiles_router
from kall.api_documents import router as documents_router
from kall.api_intelligence import router as intelligence_router
from kall.api_match_intelligence import router as match_intelligence_router
from kall.api_opportunities import router as opportunities_router
from kall.api_submissions import router as submissions_router
from kall.api_tailoring import router as tailoring_router
from kall.api_testimonials import router as testimonials_router
from kall.profile_api import router as profile_router

API_ROUTERS = (
    router,
    brief_router,
    applications_router,
    career_profiles_router,
    application_review_router,
    testimonials_router,
    profile_router,
    intelligence_router,
    match_intelligence_router,
    tailoring_router,
    documents_router,
    opportunities_router,
    submissions_router,
)


def register_api_routers(app: FastAPI) -> None:
    for api_router in API_ROUTERS:
        app.include_router(api_router, prefix="/api")
