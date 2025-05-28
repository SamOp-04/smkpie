from fastapi import APIRouter

router = APIRouter()

@router.get("/version")
async def api_version():
    return {"version": "1.0.0"}