from pydantic import BaseModel

class PredictionRequest(BaseModel):
    request_count: int
    error_rate: float
    response_time: float

class UserCreate(BaseModel):
    email: str
    password: str

class ModelUpdate(BaseModel):
    model_version: str
    s3_path: str