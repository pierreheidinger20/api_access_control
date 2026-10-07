from functools import wraps
from typing import Callable, Any
from datetime import datetime
from fastapi.responses import JSONResponse
from app.schemas.base import BaseResponse
import inspect


def auto_response(message: str = "Operation completed successfully"):
    def decorator(func: Callable) -> Callable:

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
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
                return JSONResponse(
                    status_code=400,
                    content=BaseResponse(
                        success=False,
                        message=str(e),
                        data=None,
                        timestamp=datetime.now()
                    ).model_dump(mode="json")
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
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
                return JSONResponse(
                    status_code=400,
                    content=BaseResponse(
                        success=False,
                        message=str(e),
                        data=None,
                        timestamp=datetime.now()
                    ).model_dump(mode="json")
                )

        if inspect.iscoroutinefunction(func):
            return async_wrapper

        return sync_wrapper

    return decorator