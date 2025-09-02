# app/schemas/user.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str

class SettingsUserIn(BaseModel):
    enable_notification: bool | None = None
    enable_biometric_login: bool | None = None

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    settings: SettingsUserIn | None = None

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
