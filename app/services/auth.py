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
    user_out  = UserOut(
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name
    )
    token = create_access_token(user_out.model_dump())
    
    return create_token_response(token,user_out)

def create_token_response(token: str,user_out: UserOut) -> TokenResponse:
    return TokenResponse(
        access_token=token,
        token_type=settings.token_type,
        expires_in= settings.access_token_expire_minutes * 60,  # Convert minutes to seconds
        user=user_out
    )