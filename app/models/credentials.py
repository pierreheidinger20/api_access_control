from sqlalchemy import Column, Integer, LargeBinary, ForeignKey
from app.db import db

class Credential(db.Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    aaguid = Column(LargeBinary, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    credential_id = Column(LargeBinary, nullable=False, unique=True)
    public_key = Column(LargeBinary, nullable=False)
    sign_count = Column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<Credential id={self.id} user_id={self.user_id} sign_count={self.sign_count}>"