from typing import Any, Dict

class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        http_status: int = 500,
        retryable: bool = False,
        details: Dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.http_status = http_status
        self.retryable = retryable
        self.details = details or {}
        super().__init__(self.message)

class NotFoundError(AppError):
    def __init__(self, message: str, code: str = "NOT_FOUND", details: Dict[str, Any] | None = None):
        super().__init__(code=code, message=message, http_status=404, details=details)

class UnauthorizedError(AppError):
    def __init__(self, message: str, code: str = "UNAUTHORIZED", details: Dict[str, Any] | None = None):
        super().__init__(code=code, message=message, http_status=401, details=details)

class ForbiddenError(AppError):
    def __init__(self, message: str, code: str = "FORBIDDEN", details: Dict[str, Any] | None = None):
        super().__init__(code=code, message=message, http_status=403, details=details)

class ValidationError(AppError):
    def __init__(self, message: str, code: str = "VALIDATION_ERROR", details: Dict[str, Any] | None = None):
        super().__init__(code=code, message=message, http_status=422, details=details)

class ConflictError(AppError):
    def __init__(self, message: str, code: str = "CONFLICT", details: Dict[str, Any] | None = None):
        super().__init__(code=code, message=message, http_status=409, details=details)

class RateLimitedError(AppError):
    def __init__(self, message: str, code: str = "RATE_LIMITED", details: Dict[str, Any] | None = None):
        super().__init__(code=code, message=message, http_status=429, retryable=True, details=details)

class UpstreamError(AppError):
    def __init__(self, message: str, code: str = "UPSTREAM_ERROR", details: Dict[str, Any] | None = None):
        super().__init__(code=code, message=message, http_status=502, retryable=True, details=details)

class TimeoutError(AppError):
    def __init__(self, message: str, code: str = "TIMEOUT", details: Dict[str, Any] | None = None):
        super().__init__(code=code, message=message, http_status=504, retryable=True, details=details)
