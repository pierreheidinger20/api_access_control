from fastapi import APIRouter, Depends
from app.services.auth import login_user, register_options, register_complete, login_options, login_complete
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

@router.post("/register/options")
@auto_response()
def route_register_options(username: str, display_name: str, db: Session = Depends(get_db)):
    return register_options(username, display_name, db)

@router.post("/register/complete")
@auto_response()
def route_register_complete(attestation: dict, challenge_token: str, db: Session = Depends(get_db)):
    return register_complete(attestation, challenge_token, db)

@router.post("/login/options")
@auto_response()
def route_login_options(username: str, db: Session = Depends(get_db)):
    return login_options(username, db)

@router.post("/login/complete")
@auto_response()
def route_login_complete(assertion: dict, challenge_token: str, db: Session = Depends(get_db)):
    return login_complete(assertion, challenge_token, db)
