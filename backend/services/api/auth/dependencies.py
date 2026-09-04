import uuid
from typing import Optional
from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from services.api.config import get_settings, Settings
from services.api.errors import AppError
from services.api.auth.verifier import verify_supabase_token, verify_local_token

security = HTTPBearer(auto_error=False)

class CurrentUser(BaseModel):
    id: uuid.UUID
    email: Optional[str] = None

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    settings: Settings = Depends(get_settings)
) -> CurrentUser:
    if not credentials:
        raise AppError(code="TOKEN_INVALID", message="Missing authentication token", http_status=401)
        
    token = credentials.credentials
    
    if settings.auth_mode == "supabase":
        claims = await verify_supabase_token(token)
    elif settings.auth_mode == "local":
        claims = verify_local_token(token)
    else:
        raise AppError(code="TOKEN_INVALID", message="Invalid auth mode configured", http_status=401)
        
    return CurrentUser(id=claims.sub, email=claims.email)
