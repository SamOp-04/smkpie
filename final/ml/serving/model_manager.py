import os
import logging
import joblib
from tensorflow import keras
from ml.serving.preprocessor import CyberPreprocessor

class ModelManager:
    def __init__(self, base_path="model_storage"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        
    @property
    def model_path(self):
        return os.path.join(self.base_path, "model.keras")
    
    @property
    def preprocessor_path(self):
        return os.path.join(self.base_path, "preprocessor.joblib")

    def load_assets(self):
        """Load both model and preprocessor"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        if not os.path.exists(self.preprocessor_path):
            raise FileNotFoundError(f"Preprocessor not found at {self.preprocessor_path}")
            
        model = keras.models.load_model(self.model_path)
        preprocessor = CyberPreprocessor.load(self.preprocessor_path)
        return model, preprocessor

    def save_assets(self, model, preprocessor):
        """Save both model and preprocessor"""
        model.save(self.model_path)
        preprocessor.save(self.preprocessor_path)
        logging.info(f"Model assets saved to {self.base_path}")