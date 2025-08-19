from sqlalchemy import Column, Integer, String
from app.db import db

class User(db.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=False, index=False, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)