from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    label: str
    risk_score: float
    reason: list[str]
    action: str
    message: str
