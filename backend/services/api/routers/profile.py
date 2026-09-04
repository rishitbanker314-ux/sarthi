from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.db import get_session
from services.api.auth.dependencies import CurrentUser, get_current_user
from services.api.schemas.learner_profile import LearnerProfileResponse, LearnerProfilePatchRequest
from services.api.services.profile import get_learner_profile, update_learner_profile

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])

@router.get("/learner", response_model=LearnerProfileResponse, status_code=200)
async def get_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await get_learner_profile(current_user.id, db)

@router.patch("/learner", response_model=LearnerProfileResponse, status_code=200)
async def patch_profile(
    request: LearnerProfilePatchRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await update_learner_profile(current_user.id, request, db)
