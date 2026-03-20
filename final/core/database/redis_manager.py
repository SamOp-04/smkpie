import redis.asyncio as aioredis
from core.config import settings

class RedisManager:
    def __init__(self):
        self.pool = None

    async def initialize(self):
        """Initialize async Redis connection pool"""
        if settings.REDIS_PASSWORD:
            self.pool = aioredis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
        else:
            self.pool = aioredis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )

    async def get_connection(self):
        """Get async Redis connection from pool"""
        if self.pool is None:
            await self.initialize()
        return aioredis.Redis(connection_pool=self.pool)

    async def close(self):
        """Close Redis connection pool"""
        if self.pool:
            await self.pool.disconnect()

redis_manager = RedisManager()
