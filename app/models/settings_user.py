from sqlalchemy import Column, Integer, Boolean, ForeignKey
from app.db import db

class SettingsUser(db.Base):
    __tablename__ = "settings_users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    enable_notification = Column(Boolean, nullable=False, default=False)
    enable_biometric_login = Column(Boolean, nullable=False, default=False)