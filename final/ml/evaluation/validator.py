from ml.monitoring.performance import ModelMonitor

class ModelValidator:
    def __init__(self, user_id: str):
        self.monitor = ModelMonitor(user_id)
        
    def validate_model(self, X_test, y_test):
        metrics = self.monitor.check_performance(X_test, y_test)
        return metrics['accuracy'] > 0.85