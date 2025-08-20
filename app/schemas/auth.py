from pydantic import BaseModel
from app.schemas.users import UserOut
from typing import Optional

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut 
    
class UserLogin(BaseModel):
    username: str
    password: str
    
class Config:
    from_attributes = True