from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
import logging
import time
from datetime import datetime
from ml.serving.model_manager import ModelManager
from ml.serving.predictor import CyberPredictor
from notifications.webhooks import send_webhook
from core.utils import recommended_action
from core.schemas.models import PredictionInput, PredictionResponse
from core.database.persistence import PersistenceService
from api.dependencies.auth_deps import get_authenticated_user
from core.security.action_executor import execute_action

router = APIRouter()

# Singleton ModelManager instance - loaded once at module import
model_manager = ModelManager()

@router.post("/predict/{api_key}", response_model=PredictionResponse)
async def predict(
    api_key: str,
    data: PredictionInput,
    current_user: dict = Depends(get_authenticated_user),
):
    start_time = time.time()

    try:
        if current_user.get("api_token") != api_key:
            raise HTTPException(status_code=403, detail="Token does not match requested api_key")

        # Convert validated input to dict with original column names
        input_dict = data.dict(by_alias=True)

        # Load model assets (cached after first load)
        model, preprocessor = model_manager.load_assets()

        # Convert input to DataFrame
        df = pd.DataFrame([input_dict])

        # Preprocess
        processed = preprocessor.transform(df)

        # Predict
        predictor = CyberPredictor(model)
        score = predictor.score(processed)
        is_anomaly = predictor.is_anomaly(processed)
        action = recommended_action(score)

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Save prediction to database
        prediction_id = await PersistenceService.save_prediction(
            user_id=current_user.get("id"),
            api_key=api_key,
            input_data=input_dict,
            score=score,
            is_anomaly=bool(is_anomaly),
            action=action,
            processing_time_ms=processing_time_ms,
            model_version="v1.0"
        )

        # Execute action (log for now, can be enhanced)
        await execute_action(
            action,
            {
                "user_id": current_user.get("id"),
                "api_key": api_key,
                "score": score,
                "anomaly": bool(is_anomaly),
            },
        )

        # If anomaly, send alert and save to alerts table
        if is_anomaly:
            severity = PersistenceService.get_severity_from_score(score)
            payload = {
                "anomaly": True,
                "score": score,
                "recommended_action": action,
                "prediction_id": prediction_id
            }

            # Best-effort webhook alerting
            try:
                await send_webhook(user_id=api_key, payload=payload)
                # Save successful alert
                await PersistenceService.save_alert(
                    user_id=current_user.get("id"),
                    prediction_id=prediction_id,
                    alert_type='webhook',
                    severity=severity,
                    score=score,
                    payload=payload,
                    status='sent'
                )
            except Exception as e:
                logging.warning(f"Failed to emit webhook alert for api_key={api_key}: {e}")
                # Save failed alert
                await PersistenceService.save_alert(
                    user_id=current_user.get("id"),
                    prediction_id=prediction_id,
                    alert_type='webhook',
                    severity=severity,
                    score=score,
                    payload=payload,
                    status='failed',
                    error_message=str(e)
                )

        return PredictionResponse(
            anomaly=bool(is_anomaly),
            score=score,
            recommended_action=action,
            prediction_id=prediction_id,
            timestamp=datetime.utcnow().isoformat()
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed")