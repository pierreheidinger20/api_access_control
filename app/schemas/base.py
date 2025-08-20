from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any, Dict, List
from datetime import datetime

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    timestamp: datetime = datetime.now()
    
    class Config:
        from_attributes = True