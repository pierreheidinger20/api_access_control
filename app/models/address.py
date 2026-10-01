from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from app.db import db

class Address(db.Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, unique=True, nullable=False)
    street = Column(String, nullable=False)
    number = Column(String, nullable=False)
    reference = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    coordinates = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="addresses")
