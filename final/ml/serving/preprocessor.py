import os
import pandas as pd
import joblib
from tensorflow import keras
from sklearn.preprocessing import StandardScaler


class CyberPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.columns = None  # Will store selected feature names after fitting
        
    def fit_transform(self, data: pd.DataFrame):
        self.columns = data.columns.tolist()
        return self.scaler.fit_transform(data)
    
    def transform(self, data: pd.DataFrame):
        if self.columns is None:
            raise ValueError("Preprocessor is not fitted. Call fit_transform first.")
        return self.scaler.transform(data[self.columns])
    
    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Save internal state as a dictionary
        joblib.dump({
            'scaler': self.scaler,
            'columns': self.columns
        }, path)  # <--- This is correct

    @classmethod
    def load(cls, path: str):
        saved = joblib.load(path)
        # Check if the saved object is a dictionary (new format)
        if isinstance(saved, dict):
            preprocessor = cls()
            preprocessor.scaler = saved['scaler']
            preprocessor.columns = saved['columns']
            return preprocessor
        # Handle legacy format (direct CyberPreprocessor instance)
        else:
            return saved  # <--- Only if old format exists
