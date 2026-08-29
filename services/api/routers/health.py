from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from services.api.db import get_session
from services.api.config import get_settings
import importlib.metadata

router = APIRouter()
settings = get_settings()

@router.get("/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
        
    try:
        version = importlib.metadata.version("sarathi")
    except importlib.metadata.PackageNotFoundError:
        version = "0.1.0"

    return {
        "status": "ok",
        "db": db_status,
        "version": version,
        "env": settings.env
    }
