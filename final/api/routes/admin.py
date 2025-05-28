from fastapi import APIRouter, Depends
from core.schemas.models import ModelUpdate
from ml.serving.model_manager import ModelManager
from api.dependencies.auth_deps import get_authenticated_user

router = APIRouter(dependencies=[Depends(get_authenticated_user)])

@router.post("/update-model")
async def update_model(config: ModelUpdate):
    ModelManager().update_model_version(config.s3_path)
    return {"status": "Model update initiated"}