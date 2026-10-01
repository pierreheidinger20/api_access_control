from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import db
from app.models.phone import Phone
from app.models.settings_user import SettingsUser
from app.models.user import User
from passlib.context import CryptContext
from app.schemas.users import SettingsUserOut, UserCreateByPhone, UserOut, UserUpdate,UserCreate
from app.utils.phone import normalize_phone_number, validate_phone
from app.utils.security import auth_verify_router
from app.utils.decorators import auto_response

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
    if not password:
        return None
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

@router.put("/{username}",dependencies=[Depends(auth_verify_router)])
@auto_response()
def update_user(username: str, user: UserUpdate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    settings = db.query(SettingsUser).filter(SettingsUser.user_id == existing_user.id).first()

    settings.enable_biometric_login = user.settings.enable_biometric_login
    settings.enable_notification = user.settings.enable_notification
    db.commit()
    db.refresh(settings)

    setting_out = SettingsUserOut(
        enable_notification=settings.enable_notification,
        enable_biometric_login=settings.enable_biometric_login
    )
    user_out  = UserOut(
        username=existing_user.username,
        email=existing_user.email,
        full_name=existing_user.full_name,
        settings=setting_out
    )
    return user_out

@router.post("/by-phone-number")
def create_user_by_number_phone(user_create_by_phone: UserCreateByPhone, db: Session = Depends(get_db)):
    phone_number = normalize_phone_number(user_create_by_phone.phone_number)
    validation_result = validate_phone(phone_number)
    print(validation_result)
    if not validation_result["valid"]:
        raise HTTPException(status_code=400, detail=validation_result["message"])
    existing_user = db.query(User).filter(User.phone.has(number=validation_result["international"])).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    phone = Phone(
        number=validation_result["international"],
        country=validation_result["country"],
        verified=False,
    )
    
    db_user = User(
        username=user_create_by_phone.username,
        email=user_create_by_phone.email,
        full_name=user_create_by_phone.full_name,
        hashed_password=get_password_hash(user_create_by_phone.password),
        phone=phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.refresh(phone)
    return { "phone_number": phone.number , "fullName": db_user.full_name}