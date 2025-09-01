B# Configuración de la aplicación
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración de la aplicación"""
    
    appName: str = os.getenv("APP_NAME", "API Access Control")
    web_auth_host: str = os.getenv("WEB_AUTH_HOST", "localhost")

    # Configuración general
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    
    # Base de datos
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:VIFZaNwhAriFZBvRRMGWouLGBtlwLqxT@mainline.proxy.rlwy.net:34771/railway")

    # Seguridad
    secret_key: str = os.getenv("JWT_SECRET_KEY", "123456")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    token_type: str = os.getenv("SECURITY_TYPE", "Bearer")

# Instancia global de configuración
settings = Settings()
