import uuid
import jwt
from pydantic import BaseModel
from typing import Optional

from services.api.config import get_settings
from services.api.auth.jwks import get_jwks_client
from services.api.errors import AppError

class Claims(BaseModel):
    sub: uuid.UUID
    email: Optional[str] = None
    exp: int

async def verify_supabase_token(token: str) -> Claims:
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise AppError(code="TOKEN_INVALID", message="Missing kid in token header", http_status=401, retryable=False)
            
        jwks_client = get_jwks_client()
        key = await jwks_client.get_signing_key(kid)
        
        payload = jwt.decode(
            token,
            key.key,
            algorithms=["ES256"],
            audience="authenticated",
            leeway=60,
            options={"verify_signature": True} # Explicitly true although it is the default
        )
        return Claims(**payload)
    except jwt.ExpiredSignatureError:
        raise AppError(code="TOKEN_EXPIRED", message="Token has expired", http_status=401, retryable=False)
    except jwt.PyJWKClientError:
        raise AppError(code="TOKEN_INVALID", message="Unable to find signing key", http_status=401, retryable=False)
    except jwt.InvalidTokenError:
        raise AppError(code="TOKEN_INVALID", message="Invalid token", http_status=401, retryable=False)

def verify_local_token(token: str) -> Claims:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.dev_jwt_secret,
            algorithms=["HS256"],
            leeway=60,
            options={"verify_signature": True}
        )
        return Claims(**payload)
    except jwt.ExpiredSignatureError:
        raise AppError(code="TOKEN_EXPIRED", message="Token has expired", http_status=401, retryable=False)
    except jwt.InvalidTokenError:
        raise AppError(code="TOKEN_INVALID", message="Invalid token", http_status=401, retryable=False)
