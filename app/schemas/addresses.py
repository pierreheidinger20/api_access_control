from pydantic import BaseModel

class CreateUserAddress(BaseModel):
    alias: str
    street: str
    number: str
    reference: str | None = None
    city: str
    state: str      
    postal_code: str
    country: str
    coordinates: str | None = None

class AddressOut(BaseModel):
    alias: str
    street: str
    number: str
    reference: str | None = None
    city: str
    state: str      
    postal_code: str
    country: str
    coordinates: str | None = None
