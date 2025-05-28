import pytest
import numpy as np
from data_processing.transformers.preprocessor import CyberPreprocessor

def test_preprocessing():
    preprocessor = CyberPreprocessor()
    dummy_data = {'requests': 100, 'error_rate': 0.1, 'response_time': 0.5}
    result = preprocessor.transform(dummy_data)
    assert isinstance(result, np.ndarray)
    