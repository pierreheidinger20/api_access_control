from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.utils import websafe_encode, websafe_decode
from app.config import settings

# Configuración del Relying Party (tu app)
rp = PublicKeyCredentialRpEntity(name=settings.appName, id=settings.web_auth_host)
server = Fido2Server(rp)
