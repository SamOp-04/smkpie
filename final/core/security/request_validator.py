from fastapi import HTTPException

def validate_prediction_request(data: dict):
    required = {'requests', 'error_rate', 'response_time'}
    if not required.issubset(data.keys()):
        raise HTTPException(400, "Missing required fields")
    if not 0 <= data['error_rate'] <= 1:
        raise HTTPException(400, "Invalid error rate")