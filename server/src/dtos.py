from pydantic import BaseModel

class InferenceRequest(BaseModel):
    user: str
    timestamp: int
    computer: str

class InferenceResponse(BaseModel):
    anomaly: bool
    risk_score: float