from fastapi import Depends
from core.security.auth import get_current_user
from core.security.rate_limiter import rate_limit

async def get_authenticated_user(user: dict = Depends(get_current_user)):
    await rate_limit(user['id'])
    return user