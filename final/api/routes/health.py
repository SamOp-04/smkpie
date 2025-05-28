from fastapi import APIRouter
from core.database.redis_manager import redis_manager

router = APIRouter()

@router.get("/health")
async def health_check():
    redis = redis_manager.get_connection()
    if not redis.ping():
        raise RuntimeError("Redis connection failed")
    return {"status": "ok"}