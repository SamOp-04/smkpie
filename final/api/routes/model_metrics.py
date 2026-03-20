from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import importlib

router = APIRouter()

@router.get("/metrics")
async def metrics():
    try:
        generate_latest = importlib.import_module("prometheus_client").generate_latest
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=503, detail="prometheus_client is not installed") from exc

    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )