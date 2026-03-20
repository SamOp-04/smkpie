from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
import logging
from ml.serving.model_manager import ModelManager
from ml.serving.predictor import CyberPredictor
from notifications.webhooks import send_webhook
from core.utils import recommended_action
from api.dependencies.auth_deps import get_authenticated_user
from core.security.action_executor import execute_action

router = APIRouter()

@router.post("/predict/{api_key}")
async def predict(
    api_key: str,
    data: dict,
    model_manager: ModelManager = Depends(ModelManager),
    current_user: dict = Depends(get_authenticated_user),
):
    try:
        if current_user.get("api_token") != api_key:
            raise HTTPException(status_code=403, detail="Token does not match requested api_key")

        # Load model assets
        model, preprocessor = model_manager.load_assets()
        
        # Convert input to DataFrame
        df = pd.DataFrame([data])
        
        # Preprocess
        processed = preprocessor.transform(df)
        
        # Predict
        predictor = CyberPredictor(model)
        score = predictor.score(processed)
        is_anomaly = predictor.is_anomaly(processed)
        action = recommended_action(score)

        await execute_action(
            action,
            {
                "user_id": current_user.get("id"),
                "api_key": api_key,
                "score": score,
                "anomaly": bool(is_anomaly),
            },
        )

        # Best-effort alerting hook for host application orchestration.
        if is_anomaly:
            try:
                await send_webhook(
                    user_id=api_key,
                    payload={
                        "anomaly": True,
                        "score": score,
                        "recommended_action": action,
                    },
                )
            except Exception:
                logging.warning("Failed to emit webhook alert for api_key=%s", api_key)
        
        return {
            "anomaly": bool(is_anomaly),
            "score": score,
            "recommended_action": action,
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed")