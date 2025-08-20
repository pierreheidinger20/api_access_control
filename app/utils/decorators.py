from functools import wraps
from typing import Callable, Any
from datetime import datetime
from app.schemas.base import BaseResponse
import inspect

def auto_response(message: str = "Operation completed successfully"):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> BaseResponse[Any]:
            try:
                result = await func(*args, **kwargs)
                
                if isinstance(result, BaseResponse):
                    return result
                
                return BaseResponse(
                    success=True,
                    message=message,
                    data=result,
                    timestamp=datetime.now()
                )
                
            except Exception as e:
                return BaseResponse(
                    success=False,
                    message=f"Error: {str(e)}",
                    data=None,
                    timestamp=datetime.now()
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> BaseResponse[Any]:
            try:
                result = func(*args, **kwargs)
                
                if isinstance(result, BaseResponse):
                    return result
                
                return BaseResponse(
                    success=True,
                    message=message,
                    data=result,
                    timestamp=datetime.now()
                )
                
            except Exception as e:
                return BaseResponse(
                    success=False,
                    message=f"Error: {str(e)}",
                    data=None,
                    timestamp=datetime.now()
                )
        
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator