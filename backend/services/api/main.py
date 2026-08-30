import uuid
import structlog
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from services.api.routers import health, dev_auth, me, diagnostic, profile, goals, jobs, plans, lessons, tutor, checkpoints, adaptation
from services.api.errors import AppError
from services.api.config import get_settings

logger = structlog.get_logger()

app = FastAPI(title="Sarathi API", version="0.1.0")
settings = get_settings()

@app.middleware("http")
async def global_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception("Unhandled exception", exc_info=exc, path=request.url.path)
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

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "retryable": exc.retryable,
                "details": exc.details,
            }
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters",
                "retryable": False,
                "details": {"errors": exc.errors()},
            }
        },
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "retryable": False,
                "details": {},
            }
        },
    )

app.include_router(health.router)
app.include_router(checkpoints.router)
app.include_router(lessons.router, prefix="/api/v1")
app.include_router(tutor.router, prefix="/api/v1")
app.include_router(me.router, prefix="/api/v1")
app.include_router(diagnostic.router)
app.include_router(profile.router)
app.include_router(goals.router)
app.include_router(jobs.router)
app.include_router(plans.router)
app.include_router(adaptation.router, prefix="/api/v1")
if settings.env != "production":
    from services.api.routers import dev_health
    app.include_router(dev_auth.router)
    app.include_router(dev_health.router)
