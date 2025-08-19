# Configuración de la aplicación
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración de la aplicación"""
    
    # Configuración general
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    
    # Base de datos
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:VIFZaNwhAriFZBvRRMGWouLGBtlwLqxT@mainline.proxy.rlwy.net:34771/railway")

    # Seguridad
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Instancia global de configuración
settings = Settings()
