import numpy as np
from scipy import stats

class DataDriftDetector:
    def __init__(self, reference_data):
        self.reference = reference_data
        
    def detect_drift(self, current_data):
        _, p_value = stats.ks_2samp(self.reference, current_data)
        return p_value < 0.01  # 99% confidence