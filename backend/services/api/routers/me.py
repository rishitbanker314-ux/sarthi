from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.db import get_session
from services.api.auth.dependencies import CurrentUser, get_current_user
from services.api.schemas.user import MeResponse
from services.api.services.users import get_or_create_user

router = APIRouter(prefix="/me", tags=["me"])

@router.get("", response_model=MeResponse)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get the current learner's profile.
    Lazily creates a new profile record if this is the learner's first request.
    """
    from services.api.models.learner_profile import LearnerProfile
    from sqlalchemy import select
    
    user = await get_or_create_user(session, current_user)
    
    result = await session.execute(
        select(LearnerProfile)
        .where(LearnerProfile.user_id == current_user.id)
        .order_by(LearnerProfile.profile_version.desc())
        .limit(1)
    )
    profile = result.scalar_one_or_none()
    
    return MeResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        locale=user.locale,
        created_at=user.created_at,
        has_learner_profile=profile is not None,
        profile_version=profile.profile_version if profile else None,
    )
