import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.db import get_session
from services.api.auth.dependencies import get_current_user, CurrentUser
from services.api.schemas.adaptation import AdaptationListResponse, AdaptationRespondRequest
from services.api.services.adaptation import list_adaptations, respond_to_adaptation

router = APIRouter(
    prefix="/adaptations",
    tags=["adaptation"]
)

@router.get("", response_model=AdaptationListResponse)
async def get_adaptations(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await list_adaptations(current_user.id, limit, offset, db)

@router.post("/{id}/respond", response_model=Dict[str, Any])
async def respond_adaptation(
    body: AdaptationRespondRequest,
    id: uuid.UUID = Path(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await respond_to_adaptation(current_user.id, id, body.accepted, db)
