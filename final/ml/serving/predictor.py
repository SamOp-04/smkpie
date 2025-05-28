import numpy as np
from tensorflow import keras
from core.config import settings

class CyberPredictor:
    def __init__(self, model: keras.Model):
        self.model = model
        self.threshold = settings.ANOMALY_THRESHOLD
        
    def is_anomaly(self, processed_data: np.ndarray) -> bool:
        prediction = self.model.predict(processed_data)
        return prediction[0][0] > self.threshold