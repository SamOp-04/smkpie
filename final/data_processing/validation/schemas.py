from pydantic import BaseModel, confloat, conint

class TrafficSchema(BaseModel):
    requests: conint(ge=0)
    error_rate: confloat(ge=0, le=1)
    response_time: confloat(ge=0)
class TrainingSchema(TrafficSchema):
    label: bool