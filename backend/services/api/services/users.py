from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select

from services.api.models.user import User
from services.api.auth.dependencies import CurrentUser

async def get_or_create_user(session: AsyncSession, current_user: CurrentUser) -> User:
    """
    Ensures a users row exists for current_user.id.
    Uses INSERT ... ON CONFLICT DO NOTHING to prevent race conditions.
    """
    # Insert safely
    stmt = insert(User).values(
        id=current_user.id,
        email=current_user.email,
        # Default other fields, but we only have id and email from the token
        # display_name is nullable, locale defaults to 'en'
    ).on_conflict_do_nothing(index_elements=['id'])
    
    await session.execute(stmt)
    await session.commit()
    
    # Now fetch it
    query = select(User).where(User.id == current_user.id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        # Should never happen due to the insert above unless deleted right after
        raise RuntimeError(f"User {current_user.id} not found after creation.")
        
    return user
