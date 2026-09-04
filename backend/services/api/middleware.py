import time
import uuid
import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000)
            
            # Log successful requests
            # Do NOT log bodies.
            user_id = getattr(request.state, "user_id", None)
            
            log_data = {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "request_id": request_id,
            }
            if user_id:
                log_data["user_id"] = str(user_id)
                
            logger.info("request_completed", **log_data)
            
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000)
            logger.exception("unhandled_exception", 
                             exc_info=exc, 
                             path=request.url.path, 
                             method=request.method,
                             duration_ms=duration_ms,
                             request_id=request_id)
            
            response = JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "Something went wrong on our end.",
                        "retryable": True,
                        "details": {},
                    }
                },
            )
        
        response.headers["X-Request-ID"] = request_id
        return response
