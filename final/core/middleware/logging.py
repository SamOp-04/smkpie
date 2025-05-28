from fastapi import Request
from core.utils import log_request
from data_processing.collectors.api_logs import APILogger

async def request_logger(request: Request, call_next):
    response = await call_next(request)
    user_id = request.state.user.get('id', 'anonymous') if hasattr(request.state, 'user') else 'anonymous'
    APILogger.log(request, user_id)
    return response