# app/services/auth.py
from sqlalchemy.orm import Session
from app.models import credentials
from app.models.settings_user import SettingsUser
from app.models.user import User
from app.models.credentials import Credential
from app.schemas.auth import UserLogin,TokenResponse
from app.schemas.users import SettingsUserOut, UserOut
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
from fido2.webauthn import AuthenticatorAttestationResponse, RegistrationResponse, AuthenticatorAssertionResponse
from fido2.utils import websafe_decode
from fido2 import cose
from fido2 import cbor
import cbor2
from fido2.server import PublicKeyCredentialDescriptor
from fido2.cose import CoseKey
from fido2.webauthn import AuthenticationResponse,CollectedClientData,AuthenticatorData
from fido2.webauthn import AttestedCredentialData
# from fido2.ctap2 import AttestedCredentialData
from fido2.webauthn import AuthenticatorAttachment, AuthenticationExtensionsClientOutputs,PublicKeyCredentialType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def login_user(user: UserLogin,db: Session):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    db_setting = get_create_setting_users(db, db_user)
    
    setting_out = SettingsUserOut(
        enable_notification=db_setting.enable_notification,
        enable_biometric_login=db_setting.enable_biometric_login
    )
    user_out  = UserOut(
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        settings=setting_out
    )
    token = create_access_token(user_out.model_dump())
    
    return create_token_response(token,user_out)

def verify_token(token: str) -> dict:
    try:
        payload = verify_access_token(token)
        if payload is None:
            return {"error": "Invalid token"}
        return { "is_valid": True }
    except Exception as e:
        print("Error verifying token:", e)
        return {"error": str(e)}

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
    return {"options": json.dumps(registration_data_camel, indent=4), "challenge_token": token}
        
def register_complete(attestation: dict, challenge_token: str, db: Session):
    print("Completing registration...")
    print("Attestation:", attestation)
    print("Challenge Token:", challenge_token)
    payload = verify_access_token(challenge_token)
    print("Payload:", payload)
    username = payload["username"]
    state_bytes = bytes.fromhex(payload["state"])
    state = pickle.loads(state_bytes)
    print("State:", state)
    print("llego")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not state:
        raise HTTPException(status_code=400, detail="No registration in progress")
    print("llego")

    auth_data = server.register_complete(state,attestation)
    print("Registration complete:", auth_data)

    cose_key = auth_data.credential_data.public_key
    public_key_bytes = cbor2.dumps(cose_key)
    print("auth:", auth_data)
    credential = Credential(
        user_id=user.id,
        aaguid=auth_data.credential_data.aaguid,
        credential_id=auth_data.credential_data.credential_id,
        public_key=public_key_bytes,
        sign_count=auth_data.counter
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)
    return {"status": "ok", "credential_id": credential.id}

def login_options(username: str, db: Session):
    print("username:" + username)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    credentials = db.query(Credential).filter(Credential.user_id == user.id).all()
      
    cred_list = [cred.credential_id for cred in credentials]
    print(cred_list)
    cbor2.dumps(cred_list)
    credentialsAllow = []
    for cred in credentials:  # tus credenciales guardadas en DB
        credentialsAllow.append(
            PublicKeyCredentialDescriptor(
                type="public-key",
                id=cred.credential_id  # esto DEBE ser bytes
            )
        )
    challenge, state = server.authenticate_begin(credentialsAllow)
   
    state_bytes = pickle.dumps(state)
    
    token = create_access_token({"username": username, "state": state_bytes.hex()})
    print("llego")
    registration_data_camel = convert_to_camel_case(serialize(challenge))
    return {"public_key": json.dumps(registration_data_camel), "challenge_token": token}

def b64url_to_bytes(data: str | None) -> bytes | None:
    """Decodifica base64url a bytes."""
    if not data:
        return None
    data += "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data)

def base64url_decode(data: str) -> bytes:
    # Agregar padding "=" si falta
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def login_complete(assertion: dict, challenge_token: str, db: Session):
    payload = verify_access_token(challenge_token)
    username = payload["username"]
    state_bytes = bytes.fromhex(payload["state"])
    state = pickle.loads(state_bytes)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    credentials = db.query(Credential).filter(Credential.user_id == user.id).all()
    
    authenticator_data_bytes = websafe_decode(assertion['response']['authenticatorData'])
    signature = websafe_decode(assertion['response']['signature'])

    client_data = CollectedClientData(websafe_decode(assertion['response']['clientDataJSON']))
   
    assertion_response = AuthenticatorAssertionResponse(
            client_data=client_data,
            authenticator_data=authenticator_data_bytes,
            signature=signature,
            user_handle=None 
        )
    auth_response = AuthenticationResponse(
        raw_id=websafe_decode(assertion['id']),
        response=assertion_response,
        authenticator_attachment=AuthenticatorAttachment.PLATFORM,  # o CROSS_PLATFORM
        client_extension_results=AuthenticationExtensionsClientOutputs(),
        type=PublicKeyCredentialType.PUBLIC_KEY
    )
    credenciales_fido2 = []
    for cred in credentials:
        attestedCredentialData = AttestedCredentialData.create(cred.aaguid,cred.credential_id, cbor2.loads(cred.public_key))
        credenciales_fido2.append(attestedCredentialData)

    auth_data  = server.authenticate_complete(
        state=state,
        credentials=credenciales_fido2,
        response=auth_response
    )

    authenticator_data = AuthenticatorData(authenticator_data_bytes)

    cred = db.query(Credential).filter(Credential.credential_id == auth_data.credential_id).first()
    cred.sign_count = authenticator_data.counter
    db.commit()
    db.refresh(cred)

    user_out  = UserOut(
        username=user.username,
        email=user.email,
        full_name=user.full_name
    )
    token = create_access_token(user_out.model_dump())
    
    return create_token_response(token,user_out)

def get_create_setting_users(db: Session, user: User) -> SettingsUserOut:
    settings = db.query(SettingsUser).filter(SettingsUser.user_id == user.id).first()
    if not settings:
        settings = SettingsUser(
            user_id=user.id,
            enable_notification=False,
            enable_biometric_login=False
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings