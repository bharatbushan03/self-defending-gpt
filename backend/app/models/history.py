from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class HistoryMessage(BaseModel):
    user_id: str
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
