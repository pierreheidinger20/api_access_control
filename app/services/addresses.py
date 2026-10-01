

from fastapi import HTTPException
from fastapi.datastructures import Address

from app.models.address import Address
from app.models.user import User
from app.schemas.addresses import CreateUserAddress

from sqlalchemy.orm import Session


def create_user_address(address: CreateUserAddress, payload: dict, db: Session):
    print("Payload received in create_user_address:", payload)  # Debugging line
    public_id = payload["public_id"]
    db_user = db.query(User).filter(User.public_id == public_id).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    print("User found:", db_user)  # Debugging line
    new_address = Address(
        user_id=db_user.id,
        street=address.street,
        city=address.city, 
        state=address.state,
        postal_code=address.postal_code,
        country=address.country,
        alias=address.alias,
        number=address.number,
        reference=address.reference,
        coordinates=address.coordinates
    )
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address