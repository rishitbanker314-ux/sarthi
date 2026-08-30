import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, update, func

from services.api.models.adaptation import AdaptationEvent
from services.api.models.planner import Plan
from services.api.errors import NotFoundError, AppError
from services.api.schemas.adaptation import AdaptationEventResponse, AdaptationListResponse

async def list_adaptations(user_id: uuid.UUID, limit: int, offset: int, db: AsyncSession) -> AdaptationListResponse:
    stmt = (
        select(AdaptationEvent)
        .where(AdaptationEvent.user_id == user_id)
        .order_by(desc(AdaptationEvent.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()
    
    count_stmt = select(func.count()).select_from(AdaptationEvent).where(AdaptationEvent.user_id == user_id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    
    return AdaptationListResponse(
        items=[AdaptationEventResponse.model_validate(e) for e in events],
        total=total
    )

async def respond_to_adaptation(
    user_id: uuid.UUID, 
    adaptation_id: uuid.UUID, 
    accepted: bool, 
    db: AsyncSession
) -> dict:
    result = await db.execute(
        select(AdaptationEvent).where(
            AdaptationEvent.id == adaptation_id,
            AdaptationEvent.user_id == user_id
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise NotFoundError("Adaptation event not found")
        
    if event.accepted is not None:
        raise AppError("BAD_REQUEST", "Adaptation event has already been responded to", False)
        
    event.accepted = accepted
    
    if accepted:
        # We need to activate the new plan and deactivate others for the same goal
        plan_result = await db.execute(select(Plan).where(Plan.id == event.plan_id))
        new_plan = plan_result.scalar_one_or_none()
        if not new_plan:
            raise NotFoundError("Associated plan not found")
            
        await db.execute(
            update(Plan)
            .where(Plan.goal_id == new_plan.goal_id, Plan.id != new_plan.id)
            .values(status="inactive")
        )
        new_plan.status = "active"
        
    await db.commit()
    return {"status": "success"}
