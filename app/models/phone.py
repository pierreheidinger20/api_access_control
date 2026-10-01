from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db import db

class Phone(db.Base):
    __tablename__ = "phones"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True, nullable=False)
    verified = Column(Boolean, nullable=False , default=False)
    verified_at = Column(String, nullable=True)
    country = Column(String, nullable=False)