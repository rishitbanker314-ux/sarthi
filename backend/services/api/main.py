import uuid
import structlog
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.api.routers import health, dev_auth, me, diagnostic, profile, goals, jobs, plans, lessons, tutor, checkpoints, adaptation
from services.api.errors import AppError
from services.api.config import get_settings
from services.agents.models import validate_models
from services.api.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware

from services.api.rate_limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

logger = structlog.get_logger()

app = FastAPI(title="Sarathi API", version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

settings = get_settings()
validate_models()

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected internal error occurred.",
                "retryable": True,
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
