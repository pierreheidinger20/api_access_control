# app/schemas/user.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str

class SettingsUserOut(BaseModel):
    enable_notification: bool
    enable_biometric_login: bool

class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    settings: SettingsUserOut | None = None

class Config:
    from_attributes = True
