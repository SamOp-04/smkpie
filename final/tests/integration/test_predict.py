import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.routes import predict as predict_route
from api.dependencies.auth_deps import get_authenticated_user


class _DummyPreprocessor:
    def transform(self, data):
        return data.values


class _DummyModel:
    def predict(self, processed):
        return [[0.9]]


class _DummyModelManager:
    def load_assets(self):
        return _DummyModel(), _DummyPreprocessor()


app_under_test = FastAPI()
app_under_test.include_router(predict_route.router)
client = TestClient(app_under_test)

def test_predict_endpoint():
    app_under_test.dependency_overrides[predict_route.ModelManager] = _DummyModelManager
    app_under_test.dependency_overrides[get_authenticated_user] = lambda: {
        "id": "test-user",
        "api_token": "test_token",
    }
    
    response = client.post(
        "/predict/test_token",
        headers={"Authorization": "Bearer fake_token"},
        json={"requests": 100, "error_rate": 0.1, "response_time": 0.5}
    )
    
    assert response.status_code == 200
    payload = response.json()
    assert "anomaly" in payload
    assert "score" in payload

    app_under_test.dependency_overrides.clear()