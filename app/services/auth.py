# app/services/auth.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.users import UserLogin
from app.utils.security import create_access_token,verify_password
from fastapi import Depends, HTTPException
from app.db import db
from passlib.context import CryptContext
from app.utils.security import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

