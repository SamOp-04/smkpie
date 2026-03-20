import numpy as np
from typing import Any
import torch
from core.config import settings

class CyberPredictor:
    def __init__(self, model: Any):
        self.model = model
        self.threshold = settings.ANOMALY_THRESHOLD
        
    def score(self, processed_data: np.ndarray) -> float:
        if hasattr(self.model, "predict"):
            prediction = self.model.predict(processed_data)
            return float(prediction[0][0])

        if isinstance(self.model, torch.nn.Module):
            with torch.no_grad():
                tensor = torch.tensor(processed_data, dtype=torch.float32)
                logits = self.model(tensor)
                prob = torch.sigmoid(logits).cpu().numpy()
                return float(prob[0][0])

        raise TypeError("Unsupported model type for scoring")

    def is_anomaly(self, processed_data: np.ndarray) -> bool:
        return self.score(processed_data) > self.threshold