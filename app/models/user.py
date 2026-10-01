import uuid
from sqlalchemy import Column, ForeignKey, Integer, String , UUID, text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from app.db import db

from app.models.phone import Phone
from app.models.address import Address

class User(db.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=True,
        default=uuid.uuid4,
        index=True,
        server_default=text("gen_random_uuid()"),
    )
    username = Column(String, unique=False, nullable=True)
    email = Column(String, unique=False, index=False, nullable=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)
    
    phone_id: Mapped[int] = mapped_column(
        ForeignKey("phones.id"),
        nullable=False,
        index=True
    )
    phone: Mapped["Phone"] = relationship(
        "Phone",
        passive_deletes=True,
        single_parent=True
    )
    addresses: Mapped[list["Address"]] = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete-orphan"
    )