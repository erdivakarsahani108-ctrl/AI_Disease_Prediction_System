"""Application configuration."""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "AI Disease Prediction System"
    APP_VERSION: str = "4.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_SECRET"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database — SQLite by default (zero-config). Set to PostgreSQL for production.
    # Example prod: postgresql://user:pass@host:5432/disease_ai
    DATABASE_URL: str = "sqlite:///./disease_ai.db"
    DATABASE_URL_SYNC: str = "sqlite:///./disease_ai.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Medical safety
    EMERGENCY_KEYWORDS: List[str] = [
        "chest pain", "heart attack", "stroke", "suicide", "bleeding heavily",
        "can't breathe", "unconscious", "seizure", "severe allergic",
        "छाती में दर्द", "दिल का दौरा", "स्ट्रोक", "सांस नहीं आ रही",
        "behoshi", "seizure", "emergency"
    ]

    # Supported languages
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi", "hinglish", "bhojpuri"]

    # Medical systems
    MEDICAL_SYSTEMS: List[str] = [
        "allopathy", "ayurveda", "homeopathy", "unani", "siddha",
        "yoga_naturopathy", "naturopathy", "acupuncture", "acupressure",
        "physiotherapy", "chiropractic", "aromatherapy", "reiki"
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
