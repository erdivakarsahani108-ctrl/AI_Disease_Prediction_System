"""
AI-Based Disease Prediction System v2 — FastAPI entrypoint.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.middleware import CorrelationIdMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1 import router as v1_router
from app.core.rate_limit import rate_limit_dependency
from app.core.config import get_settings
from app.db.database import SessionLocal, init_db
from app.ml.predictor import get_predictor
from app.services.knowledge_seed import seed_knowledge

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        n = seed_knowledge(db)
        if n:
            print(f"Seeded {n} knowledge documents")
    finally:
        db.close()
    get_predictor()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Educational AI platform for disease prediction support, nutrition guidance "
        "and multilingual medical knowledge assistance. "
        "NOT a substitute for professional medical care."
    ),
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"] if settings.DEBUG else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix=settings.API_V1_PREFIX, dependencies=[])  # rate limit applied per-route optionally


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
        "features": [
            "disease-prediction", "multilingual-chatbot", "bmi-bmr-nutrition",
            "persistent-auth", "prediction-history", "knowledge-rag", "dashboard",
        ],
        "disclaimer": (
            "Educational / research use only. Not for clinical diagnosis. "
            "Always consult qualified healthcare professionals."
        ),
    }
