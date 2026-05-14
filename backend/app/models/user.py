from pydantic import BaseModel, Field

class UserModel(BaseModel):
    user_id: str = Field(...)
    trust_score: float = Field(default=50.0, ge=0, le=100)
    # ge=0 means greater than or equal to 0
    # le=100 means less than or equal to 100

class UserUpdateResponse(BaseModel):
    user_id: str
    trust_score: float
    message: str
