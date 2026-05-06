from pydantic import BaseModel

class ChatResponse(BaseModel):
    response: str | None
    action: str
    message: str
    risk_score: int
    trust_score: int
    reauth_required: bool
