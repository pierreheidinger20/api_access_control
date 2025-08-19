from fastapi import APIRouter
from app.services.auth import login_user
from app.schemas.users import UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(user: UserLogin):
    return login_user(user)

