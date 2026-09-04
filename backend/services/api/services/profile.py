import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.api.errors import NotFoundError
from services.api.models.learner_profile import LearnerProfile
from services.api.schemas.learner_profile import LearnerProfileResponse, LearnerProfilePatchRequest
from services.api.models.user import User

async def get_latest_profile(user_id: uuid.UUID, db: AsyncSession) -> LearnerProfile:
    result = await db.execute(
        select(LearnerProfile)
        .where(LearnerProfile.user_id == user_id)
        .order_by(LearnerProfile.profile_version.desc())
        .limit(1)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Learner profile not found.")
    return profile

async def get_learner_profile(user_id: uuid.UUID, db: AsyncSession) -> LearnerProfileResponse:
    profile = await get_latest_profile(user_id, db)
    return LearnerProfileResponse.model_validate(profile)

async def update_learner_profile(user_id: uuid.UUID, patch_data: LearnerProfilePatchRequest, db: AsyncSession) -> LearnerProfileResponse:
    old_profile = await get_latest_profile(user_id, db)
    
    # Merge fields
    new_data = {
        "user_id": user_id,
        "profile_version": old_profile.profile_version + 1,
        "prior_knowledge": old_profile.prior_knowledge,
        "pace": old_profile.pace,
        "representation_pref": old_profile.representation_pref,
        "scaffolding_pref": old_profile.scaffolding_pref,
        "depth_pref": old_profile.depth_pref,
        "motivation": old_profile.motivation,
        "session_minutes": old_profile.session_minutes,
        "language": old_profile.language,
        "accessibility": old_profile.accessibility,
    }
    
    patch_dict = patch_data.model_dump(exclude_unset=True)
    for k, v in patch_dict.items():
        if v is not None:
            new_data[k] = v
            
    # Create new profile row
    new_profile = LearnerProfile(**new_data)
    db.add(new_profile)
    
    # Update the user's profile_version if we are tracking it there?
    # No, wait, in Context.md/Backend_Instructions_1.md we saw:
    # "users (id, ... profile_version)" -> wait, does users table have profile_version?
    # Let's check `User` model.
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user and hasattr(user, "profile_version"):
        # Wait, the User table in our DB actually didn't have profile_version! We checked it earlier.
        # So we don't need to update it here.
        pass
        
    await db.commit()
    await db.refresh(new_profile)
    
    return LearnerProfileResponse.model_validate(new_profile)
