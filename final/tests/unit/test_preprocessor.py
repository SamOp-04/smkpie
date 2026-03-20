import pytest
import numpy as np
import pandas as pd
from ml.serving.preprocessor import CyberPreprocessor

def test_preprocessing():
    preprocessor = CyberPreprocessor()
    training_data = pd.DataFrame([
        {"requests": 100, "error_rate": 0.1, "response_time": 0.5},
        {"requests": 120, "error_rate": 0.2, "response_time": 0.7},
    ])
    preprocessor.fit_transform(training_data)

    inference_data = pd.DataFrame([
        {"requests": 110, "error_rate": 0.15, "response_time": 0.6}
    ])
    result = preprocessor.transform(inference_data)
    assert isinstance(result, np.ndarray)
    assert result.shape == (1, 3)
    