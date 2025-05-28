from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.database.supabase_crud import SupabaseCRUD

router = APIRouter(tags=["Settings"], prefix="/settings")

class MonitorSettings(BaseModel):
    interval_seconds: int
    threshold: float

@router.post("/{token}")
async def set_monitoring(token: str, settings: MonitorSettings):
    crud = SupabaseCRUD()
    user = crud.get_user_by_token(token)
    if not user:
        raise HTTPException(404, "User not found")
    crud.upsert_monitor_settings(user["id"], settings.dict())
    return {"status": "ok"}

@router.get("/{token}", response_model=MonitorSettings)
async def get_monitoring(token: str):
    crud = SupabaseCRUD()
    user = crud.get_user_by_token(token)
    if not user:
        raise HTTPException(404, "User not found")
    settings = crud.get_monitor_settings(user["id"])
    if not settings:
        # You can choose sensible defaults here instead of 404
        raise HTTPException(404, "No settings found")
    return MonitorSettings(**settings)
