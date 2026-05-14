from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class SecurityLog(BaseModel):
    user_id: str
    prompt: str
    label: str
    risk_score: float
    action: str
    reauth_required: bool
    reasons: List[str]
    attack_type: str
    trust_score: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
