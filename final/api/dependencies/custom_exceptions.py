from fastapi import HTTPException

class ModelLoadingError(HTTPException):
    def __init__(self):
        super().__init__(500, "Failed to load model")

class DataValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(400, f"Invalid data format: {detail}")