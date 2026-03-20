"""
Middleware to enforce block/throttle actions set by the action executor.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from core.database.redis_manager import redis_manager
import logging


class ActionEnforcementMiddleware(BaseHTTPMiddleware):
    """Enforces block and throttle actions by checking Redis state"""

    async def dispatch(self, request: Request, call_next):
        # Extract API key from path parameters or headers
        api_key = request.path_params.get('api_key')
        if not api_key and 'X-API-Key' in request.headers:
            api_key = request.headers['X-API-Key']

        if api_key:
            redis = await redis_manager.get_connection()

            # Check if API key is blocked
            if await redis.exists(f"blocked:{api_key}"):
                ttl = await redis.ttl(f"blocked:{api_key}")
                logging.warning(f"Blocked request from api_key={api_key}, TTL={ttl}s")
                raise HTTPException(
                    status_code=403,
                    detail=f"API key temporarily blocked due to suspicious activity. Try again in {ttl} seconds."
                )

            # Check if API key is throttled
            if await redis.exists(f"throttled:{api_key}"):
                # Apply stricter rate limit for throttled keys
                throttle_key = f"throttle_limit:{api_key}"
                current = await redis.incr(throttle_key)
                if current == 1:
                    await redis.expire(throttle_key, 60)

                # Reduced limit: 10 requests per minute (vs normal limit)
                if current > 10:
                    ttl = await redis.ttl(f"throttled:{api_key}")
                    logging.warning(f"Throttled request from api_key={api_key}, count={current}")
                    raise HTTPException(
                        status_code=429,
                        detail=f"API key is throttled. Reduced rate limit in effect for {ttl} seconds."
                    )

        # Process the request
        response = await call_next(request)
        return response
