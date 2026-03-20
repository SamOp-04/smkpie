from pydantic import BaseModel, Field
from typing import Optional

class PredictionInput(BaseModel):
    """18 required network traffic features for anomaly detection"""
    flow_duration: float = Field(alias="Flow Duration", ge=0)
    total_fwd_packet: int = Field(alias="Total Fwd Packet", ge=0)
    total_bwd_packets: int = Field(alias="Total Bwd Packets", ge=0)
    fwd_packets_s: float = Field(alias="Fwd Packets/s", ge=0)
    bwd_packets_s: float = Field(alias="Bwd Packets/s", ge=0)
    flow_packets_s: float = Field(alias="Flow Packets/s", ge=0)
    fwd_header_length: int = Field(alias="Fwd Header Length", ge=0)
    bwd_header_length: int = Field(alias="Bwd Header Length", ge=0)
    fwd_packet_length_mean: float = Field(alias="Fwd Packet Length Mean", ge=0)
    bwd_packet_length_mean: float = Field(alias="Bwd Packet Length Mean", ge=0)
    packet_length_mean: float = Field(alias="Packet Length Mean", ge=0)
    packet_length_std: float = Field(alias="Packet Length Std", ge=0)
    flow_iat_mean: float = Field(alias="Flow IAT Mean", ge=0)
    flow_iat_std: float = Field(alias="Flow IAT Std", ge=0)
    active_mean: float = Field(alias="Active Mean", ge=0)
    idle_mean: float = Field(alias="Idle Mean", ge=0)
    fwd_init_win_bytes: int = Field(alias="FWD Init Win Bytes", ge=0)
    bwd_init_win_bytes: int = Field(alias="Bwd Init Win Bytes", ge=0)

    class Config:
        allow_population_by_field_name = True  # Accept both snake_case and original names

class PredictionResponse(BaseModel):
    """Response from prediction endpoint"""
    anomaly: bool
    score: float
    recommended_action: str
    prediction_id: int
    timestamp: str

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