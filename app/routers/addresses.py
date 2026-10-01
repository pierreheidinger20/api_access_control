from fastapi import APIRouter, Body, Depends

from app.db import db
from app.schemas.addresses import CreateUserAddress, AddressOut
from app.services.addresses import create_user_address
from app.utils.decorators import auto_response
from sqlalchemy.orm import Session
from app.utils.security import auth_verify_router

router = APIRouter(prefix="/addresses", tags=["addresses"])

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@router.post("")
@auto_response()
def create_address(userAddress: CreateUserAddress, db: Session = Depends(get_db),payload: dict = Depends(auth_verify_router)):
    address = create_user_address(userAddress, payload, db)
    print("Address created:", address)  # Debugging line
    address_out = AddressOut(
        alias=address.alias,
        street=address.street,
        number=address.number,
        reference=address.reference,
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        country=address.country,
        coordinates=address.coordinates
    )
    return address_out