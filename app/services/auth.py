# app/services/auth.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.credentials import Credential
from app.schemas.auth import UserLogin,TokenResponse
from app.schemas.users import UserOut
from app.utils.security import create_access_token,verify_password,verify_access_token
from fastapi import HTTPException
from app.db import db
from passlib.context import CryptContext
from app.utils.security import create_access_token
from app.config import settings
from app.utils.webauthn import server
from fido2.webauthn import PublicKeyCredentialUserEntity
import pickle
from fido2.utils import websafe_encode
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
import json
import base64
from dataclasses import asdict, is_dataclass


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
    
def serialize(obj):
    if is_dataclass(obj):
        return {k: serialize(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    elif hasattr(obj, 'value'):  # Para enums
        return obj.value
    elif isinstance(obj, list):
        return [serialize(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    else:
        return obj
    
def to_camel_case(snake_str):
    if not snake_str:  # Manejar cadenas vacías
        return snake_str
    
    # Dividir por guiones bajos y filtrar partes vacías
    parts = [part for part in snake_str.split('_') if part]
    
    if not parts:  # Si no hay partes válidas, devolver cadena vacía
        return ''
    
    # Mantener la primera parte en minúsculas y capitalizar las siguientes
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

def convert_to_camel_case(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            # Asegurarse de que la clave sea una cadena
            new_key = to_camel_case(str(k))
            new_obj[new_key] = convert_to_camel_case(v)
        return new_obj
    elif isinstance(obj, list):
        return [convert_to_camel_case(item) for item in obj]
    elif isinstance(obj, (set, tuple)):
        return [convert_to_camel_case(item) for item in obj]
    else:
        # Devolver valores no modificados (incluye None, strings, números, etc.)
        return obj
    
def register_options(username: str, display_name: str, db: Session):
    # Crea usuario para el registro WebAuthn
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_id_bytes = user.id.to_bytes(8, "big")
    
    user = PublicKeyCredentialUserEntity(
        id=user_id_bytes,
        name=username,
        display_name=display_name
    )
    registration_data, state = server.register_begin(user, user_verification="required")
    
    registration_data_camel = convert_to_camel_case(serialize(registration_data))
    # print(registration_data_camel)
    state_bytes = pickle.dumps(state)
    # print(serialize(registration_data))
    # json_data = json.dumps(serialize(registration_data_camel), indent=4)
    # print(json_data)
    token = create_access_token(
        {"state": state_bytes.hex(), "username": username}
    )
    # print(registration_data)
    return {"publicKey": json.dumps(registration_data_camel, indent=4), "challenge_token": token}
        
def register_complete(attestation: dict, challenge_token: str, db: Session):
    payload = verify_access_token(challenge_token)
    username = payload["username"]
    state_bytes = bytes.fromhex(payload["state"])
    state = pickle.loads(state_bytes)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not state:
        raise HTTPException(status_code=400, detail="No registration in progress")
    auth_data = server.register_complete(state, attestation)
    credential = Credential(
        user_id=user.id,
        credential_id=auth_data.credential_id,
        public_key=auth_data.public_key,
        sign_count=auth_data.sign_count
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)
    return {"status": "ok", "credential_id": credential.id}

def login_options(username: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    credentials = db.query(Credential).filter(Credential.user_id == user.id).all()

    cred_list = [cred.credential_id for cred in credentials]
    challenge, state = server.authenticate_begin(cred_list)

    state_bytes = pickle.dumps(state)
    token = create_access_token({"username": username, "state": state_bytes.hex()})

    return {"publicKey": challenge, "challenge_token": token}

def login_complete(assertion: dict, challenge_token: str, db: Session):
    payload = verify_access_token(challenge_token)
    username = payload["username"]
    state_bytes = bytes.fromhex(payload["state"])

    state = pickle.loads(state_bytes)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    credentials = db.query(Credential).filter(Credential.user_id == user.id).all()
    cred_list = [
        {
            "credential_id": cred.credential_id,
            "public_key": cred.public_key,
            "sign_count": cred.sign_count
        } for cred in credentials
    ]

    auth_data = server.authenticate_complete(state, cred_list, assertion)

    cred = db.query(Credential).filter(Credential.credential_id == auth_data.credential_id).first()
    cred.sign_count = auth_data.sign_count
    db.commit()
    db.refresh(cred)

    return {"status": "ok", "message": "User authenticated"}
