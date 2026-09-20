from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.exceptions import TwinQMapException
from backend.core.logging import general_logger
import traceback
import time

class GlobalErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware to catch all unhandled exceptions and custom
    TwinQMapException errors, returning standardized RFC 7807 error responses.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except TwinQMapException as exc:
            # Handle custom application exceptions
            general_logger.warning(
                f"App error occurred: {exc.message} | Path: {request.url.path} | Status Code: {exc.status_code}"
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "type": f"https://twinqmap.org/errors/{exc.__class__.__name__}",
                    "title": exc.__class__.__name__,
                    "status": exc.status_code,
                    "detail": exc.message,
                    "instance": request.url.path,
                    "error_details": exc.detail
                },
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*"
                }
            )
        except Exception as exc:
            # Handle unexpected system errors
            tb = traceback.format_exc()
            general_logger.error(
                f"Unhandled Exception in request pipeline! Path: {request.url.path} | Error: {str(exc)}\n{tb}"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "type": "https://twinqmap.org/errors/InternalServerError",
                    "title": "Internal Server Error",
                    "status": 500,
                    "detail": "An unexpected error occurred on the server.",
                    "instance": request.url.path
                },
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*"
                }
            )
