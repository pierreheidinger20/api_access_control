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
        from app import models
        self.Base.metadata.create_all(bind=self.engine)

# Crear instancia global
db = Database()
