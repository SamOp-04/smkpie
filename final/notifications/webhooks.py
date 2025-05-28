import httpx
from core.config import settings

async def send_webhook(user_id: str, payload: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.SUPABASE_URL}/rest/v1/webhooks",
                json={
                    "user_id": user_id,
                    "payload": payload
                },
                headers={
                    "apikey": settings.SUPABASE_KEY,
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            print(f"Webhook failed: {str(e)}")