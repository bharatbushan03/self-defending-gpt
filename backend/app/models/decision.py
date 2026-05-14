from pydantic import BaseModel, Field
from typing import Literal

class Decision(BaseModel):
    action: Literal["ALLOW", "WARN", "BLOCK"]
    message: str
    reauth_required: bool = Field(default=False)
