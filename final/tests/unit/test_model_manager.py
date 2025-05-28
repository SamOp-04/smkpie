import pytest
from ml.serving.model_manager import ModelManager
from unittest.mock import patch

@patch('boto3.client')
def test_model_loading(mock_s3):
    mock_s3.return_value.download_file.return_value = None
    manager = ModelManager()
    model, preprocessor = manager.load_model("test_user")
    assert model is not None