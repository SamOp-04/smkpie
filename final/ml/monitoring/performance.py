from ml.serving.model_manager import ModelManager
from data_processing.transformers.drift_detector import DataDriftDetector

class ModelMonitor:
    def __init__(self, user_id):
        self.user_id = user_id
        self.model, self.preprocessor = ModelManager().load_model(user_id)
        
    def check_performance(self, X_test, y_test):
        loss, accuracy = self.model.evaluate(X_test, y_test)
        return {"accuracy": accuracy, "loss": loss}
    
    def check_data_drift(self, current_data):
        reference = self.preprocessor.get_reference_distribution()
        return DataDriftDetector(reference).detect_drift(current_data)