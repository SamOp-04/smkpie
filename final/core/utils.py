import logging
import secrets
from typing import Optional
from fastapi import Request
from core.database.redis_manager import redis_manager

def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

def generate_api_token() -> str:
    return secrets.token_urlsafe(32)

def get_redis_connection():
    return redis_manager.get_connection()