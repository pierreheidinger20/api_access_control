from psycopg2 import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

class Database:
    def __init__(self):
        self.SQLALCHEMY_DATABASE_URL = settings.database_url
        self.engine = create_engine(self.SQLALCHEMY_DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()
    
    def init_db(self):
        try:
            connection = self.engine.connect()
            from app.models import user 
            self.Base.metadata.create_all(bind=self.engine)
            self._initialized = True
            print("✅ Conexión a la DB exitosa y tablas creadas o ya existen")
            connection.close()
        except OperationalError as e:
            print(f"❌ Error conectando a la DB: {e}")
            raise e
        

# Crear instancia global
db = Database()
