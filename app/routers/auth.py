from fastapi import APIRouter, Depends
from app.services.auth import login_user
from app.schemas.auth import UserLogin
from sqlalchemy.orm import Session
from app.db import db
from app.utils.decorators import auto_response

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@router.post("/login")
@auto_response()
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(user, db)

