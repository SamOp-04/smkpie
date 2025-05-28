from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import APIRouter, Depends
router = APIRouter()

class LogData(BaseModel):
    timestamp: str
    message: str

@router.post("/logs/{token}")
async def log_data(token: str, log: LogData):
    # You can store the log data or just print it for now
    print(f"Log received for token {token}: {log.timestamp} - {log.message}")
    
    # Respond with a success message
    return {"status": "success", "message": "Log received"}
