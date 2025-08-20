# app/schemas/user.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str

class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

class Config:
    from_attributes = True
    


