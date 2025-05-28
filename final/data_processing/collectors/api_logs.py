from core.database import supabase
from core.utils import log_request

class APILogger:
    @staticmethod
    def log(request: Request, user_id: str):
        log_request(request, user_id)
        supabase.table("api_logs").insert({
            "user_id": user_id,
            "endpoint": str(request.url),
            "method": request.method
        }).execute()