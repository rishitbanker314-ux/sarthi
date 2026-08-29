import uuid
import time
import jwt
from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr

from services.api.config import get_settings, Settings

router = APIRouter(prefix="/dev/auth", tags=["dev"])

NAMESPACE_DEV_AUTH = uuid.UUID("12345678-1234-5678-1234-567812345678")

def dev_user_id(email: str) -> uuid.UUID:
    """Deterministic UUID generation for dev environments."""
    return uuid.uuid5(NAMESPACE_DEV_AUTH, email.lower())

class DevAuthRequest(BaseModel):
    email: EmailStr

@router.post("/token")
async def generate_dev_token(req: DevAuthRequest, settings: Settings = Depends(get_settings)):
    user_id = dev_user_id(req.email)
    
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "email": req.email,
        "iat": now,
        "exp": now + (24 * 3600), # 24 hours
        "nbf": now
    }
    
    token = jwt.encode(
        payload,
        settings.dev_jwt_secret,
        algorithm="HS256"
    )
    
    return {"access_token": token, "token_type": "bearer"}
