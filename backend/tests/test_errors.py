import pytest
from services.api.errors import (
    AppError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ValidationError,
    ConflictError,
    RateLimitedError,
    UpstreamError,
    TimeoutError
)

def test_app_error_subclass_http_status():
    errors = [
        NotFoundError("test"),
        UnauthorizedError("test"),
        ForbiddenError("test"),
        ValidationError("test"),
        ConflictError("test"),
        RateLimitedError("test"),
        UpstreamError("test"),
        TimeoutError("test")
    ]
    
    for error in errors:
        assert isinstance(error.http_status, int)
        assert 100 <= error.http_status <= 599
