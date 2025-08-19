from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import db
from app.models.user import User
from passlib.context import CryptContext
from app.schemas.users import UserCreate

router = APIRouter(
    prefix="/users",       # todas las rutas de este router comienzan con /users
    tags=["users"]         # etiqueta para documentación automática
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependencia para obtener sesión
def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# Función para hashear contraseña
def get_password_hash(password):
    return pwd_context.hash(password)

# Endpoint para crear usuario
@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}
