import asyncio
from core.database.redis_manager import redis_manager

class WebTrafficCollector:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.redis = redis_manager.get_connection()
        
    async def collect(self, interval: int):
        while True:
            # Simulated traffic collection
            traffic_data = self._fetch_traffic()
            self.redis.lpush(f"traffic:{self.user_id}", str(traffic_data))
            await asyncio.sleep(interval)
    
    def _fetch_traffic(self):
        return {
            "requests": 150,
            "response_time": 0.45,
            "error_rate": 0.02
        }