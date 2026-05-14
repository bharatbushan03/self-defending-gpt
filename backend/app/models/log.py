from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class SecurityLog(BaseModel):
    user_id: str
    prompt: str
    label: str
    risk_score: float
    action: str
    reauth_required: bool
    reasons: List[str]
    attack_type: Optional[str] = None
    trust_score: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
