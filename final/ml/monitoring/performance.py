from ml.serving.model_manager import ModelManager
from ml.serving.predictor import CyberPredictor
from data_processing.transformers.drift_detector import DataDriftDetector
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class ModelMonitor:
    def __init__(self, user_id):
        self.user_id = user_id
        self.model, self.preprocessor = ModelManager().load_assets()
        
    def check_performance(self, X_test, y_test):
        predictor = CyberPredictor(self.model)
        scores = [predictor.score([row]) for row in X_test]
        preds = [1 if score >= 0.5 else 0 for score in scores]
        return {
            "accuracy": float(accuracy_score(y_test, preds)),
            "precision": float(precision_score(y_test, preds, zero_division=0)),
            "recall": float(recall_score(y_test, preds, zero_division=0)),
            "f1": float(f1_score(y_test, preds, zero_division=0)),
        }
    
    def check_data_drift(self, current_data):
        reference = self.preprocessor.get_reference_distribution()
        return DataDriftDetector(reference).detect_drift(current_data)