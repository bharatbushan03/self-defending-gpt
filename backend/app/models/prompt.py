from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str
    user_id: str

class PromptResponse(BaseModel):
    label: str
    risk_score: int
    reason: list[str]
    action: str
    message: str
    trust_score: int
    reauth_required: bool