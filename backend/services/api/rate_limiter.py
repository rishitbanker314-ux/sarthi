from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import Request

# Simple rate limiter using the client IP address.
# In production with authentication, it's often better to rate limit by user_id if present.
# Here we'll default to IP, but we can customize the key function to use user_id.

def get_rate_limit_key(request: Request) -> str:
    # Use user_id if available (from AuthMiddleware), otherwise fallback to IP
    if hasattr(request.state, "user_id") and request.state.user_id:
        return str(request.state.user_id)
    return get_remote_address(request)

limiter = Limiter(key_func=get_rate_limit_key)
