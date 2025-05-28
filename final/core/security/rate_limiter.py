from fastapi import HTTPException
from core.database.redis_manager import redis_manager
from core.config import settings

async def rate_limit(user_id: str):
    redis = redis_manager.get_connection()
    key = f"rate_limit:{user_id}"
    current = redis.incr(key)
    if current > settings.MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(429, "Rate limit exceeded")
    redis.expire(key, 60)