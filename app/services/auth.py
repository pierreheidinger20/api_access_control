# app/services/auth.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserLogin,TokenResponse
from app.schemas.users import UserOut
from app.utils.security import create_access_token,verify_password
from fastapi import HTTPException
from app.db import db
from passlib.context import CryptContext
from app.utils.security import create_access_token
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def login_user(user: UserLogin,db: Session):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = create_access_token({"sub": db_user.username})
    
    return create_token_response(token,db_user)

def create_token_response(token: str,user: User) -> TokenResponse:
    userOut  = UserOut(
        username=user.username,
        email=user.email,
        full_name=user.full_name
    )
    return TokenResponse(
        access_token=token,
        token_type=settings.token_type,
        expires_in= settings.access_token_expire_minutes * 60,  # Convert minutes to seconds
        user=userOut
    )