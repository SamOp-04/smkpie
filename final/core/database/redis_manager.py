import redis
from core.config import settings

class RedisManager:
    def __init__(self):
        if settings.REDIS_PASSWORD:
            self.pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
        else:
            self.pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
    
    def get_connection(self):
        return redis.Redis(connection_pool=self.pool)

redis_manager = RedisManager()
