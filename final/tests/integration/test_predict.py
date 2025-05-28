import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_predict_endpoint(mocker):
    mocker.patch("ml.serving.model_manager.ModelManager.load_model", 
                return_value=(lambda x: [[0.1]], None))
    
    response = client.post(
        "/predict/test_token",
        headers={"Authorization": "Bearer fake_token"},
        json={"data": "test"}
    )
    
    assert response.status_code == 200
    assert "prediction" in response.json()