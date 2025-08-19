from fastapi import APIRouter, Depends
from app.services.auth import login_user
from app.schemas.users import UserLogin
from sqlalchemy.orm import Session
from app.db import db

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@router.post("/login")
def login(user: UserLogin,db: Session = Depends(get_db)):
    return login_user(user,db)

