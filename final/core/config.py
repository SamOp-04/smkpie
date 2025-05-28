# core/config.py

import secrets
from datetime import datetime
from fastapi import Request
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # AWS / S3 model storage
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    S3_BUCKET: str

    # Application settings
    MODEL_UPDATE_INTERVAL: int
    ANOMALY_THRESHOLD: float
    MAX_REQUESTS_PER_MINUTE: int

    # Email/SMTP config for alerts
    EMAIL_SENDER: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# instantiate once, reuse everywhere
settings = Settings()

def generate_api_token() -> str:
    return secrets.token_urlsafe(32)

def log_request(request: Request, user_id: str):
    print(f"{datetime.utcnow()} - {user_id} - {request.method} {request.url}")
