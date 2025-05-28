from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
import numpy as np
import logging
from ml.serving.model_manager import ModelManager
from ml.serving.predictor import CyberPredictor

router = APIRouter()

@router.post("/predict/{api_key}")
async def predict(
    api_key: str,
    data: dict,
    model_manager: ModelManager = Depends(ModelManager)
):
    try:
        # Load model assets
        model, preprocessor = model_manager.load_assets()
        
        # Convert input to DataFrame
        df = pd.DataFrame([data])
        
        # Preprocess
        processed = preprocessor.transform(df)
        
        # Predict
        predictor = CyberPredictor(model)
        is_anomaly = predictor.is_anomaly(processed)
        score = float(model.predict(processed)[0][0])
        
        return {
    "anomaly": bool(is_anomaly),  # Convert numpy bool to Python bool
    "score": score
}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Prediction failed")