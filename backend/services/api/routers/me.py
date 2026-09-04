from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.db import get_session
from services.api.auth.dependencies import CurrentUser, get_current_user
from services.api.schemas.user import MeResponse
from services.api.schemas.signal import SignalResponse
from services.api.schemas.mastery import MasteryStateResponse
from services.api.services.users import get_or_create_user
from services.api.models.lesson_execution import Signal, MasteryState
from typing import List

router = APIRouter(tags=["me"])

@router.get("/me", response_model=MeResponse)
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

@router.get("/users/me/signals", response_model=List[SignalResponse])
async def get_my_signals(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    26 GET /api/v1/users/me/signals
    """
    from sqlalchemy import select
    result = await session.execute(
        select(Signal)
        .where(Signal.user_id == current_user.id)
        .order_by(Signal.created_at.desc())
    )
    signals = result.scalars().all()
    
    return [
        SignalResponse(
            id=s.id,
            user_id=s.user_id,
            lesson_id=s.lesson_id,
            block_id=s.block_id,
            type=s.type,
            value=s.value,
            created_at=s.created_at
        ) for s in signals
    ]

@router.get("/users/me/progress", response_model=List[MasteryStateResponse])
async def get_my_progress(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    27 GET /api/v1/users/me/progress
    """
    from sqlalchemy import select
    result = await session.execute(
        select(MasteryState)
        .where(MasteryState.user_id == current_user.id)
    )
    states = result.scalars().all()
    
    return [
        MasteryStateResponse(
            id=s.id,
            user_id=s.user_id,
            concept_id=s.concept_id,
            score=s.score,
            confidence=s.confidence,
            attempts=s.attempts,
            created_at=s.created_at,
            last_seen_at=s.last_seen_at
        ) for s in states
    ]
