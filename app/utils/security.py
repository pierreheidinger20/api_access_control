from datetime import datetime, timedelta
from fastapi import HTTPException,Header,status
from jose import jwt
from app.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=str(e))

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def auth_verify_router(authorization: str = Header(...)):
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != settings.token_type.lower():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme.")
    payload = verify_access_token(token)
    return payload
