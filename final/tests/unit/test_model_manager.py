import pytest
from ml.serving.model_manager import ModelManager
from unittest.mock import patch

@patch("ml.serving.preprocessor.CyberPreprocessor.load")
@patch("ml.serving.model_manager.torch.load")
@patch("ml.serving.model_manager.os.path.exists", return_value=True)
def test_model_loading(mock_exists, mock_torch_load, mock_preprocessor_load):
    mock_torch_load.return_value = {
        "state_dict": {},
        "input_dim": 18,
    }
    mock_preprocessor_load.return_value = object()
    with patch("ml.serving.model_manager._InferenceMLP.load_state_dict"):
        manager = ModelManager()
        model, preprocessor = manager.load_assets()

    assert model is not None
    assert preprocessor is not None