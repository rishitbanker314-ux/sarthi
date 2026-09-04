from typing import Any, List
import asyncio
from services.api.rate_limiter import limiter
import uuid
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from services.api.db import get_session
from services.api.auth.dependencies import get_current_user, CurrentUser
from services.api.errors import AppError, NotFoundError
from services.api.models import Lesson, LessonContent, User, LearnerProfile, Signal, Module, Plan, Goal
from services.agents.tutor import TutorAgent
from services.agents.schemas import ContentBlock
from services.api.schemas.lesson import ReexplainRequest
from services.api.sse import stream_with_heartbeat
from fastapi.responses import StreamingResponse
from services.api.schemas.signal import SignalCreate, SignalResponse

router = APIRouter(prefix="/lessons", tags=["lessons"])
tutor_agent = TutorAgent()

async def get_user_lesson(lesson_id: UUID, user_id: UUID, db: AsyncSession) -> Lesson:
    query = (
        select(Lesson)
        .join(Module)
        .join(Plan)
        .join(Goal)
        .where(
            Lesson.id == lesson_id,
            Goal.user_id == user_id
        )
    )
    result = await db.execute(query)
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise NotFoundError("Lesson not found")
    return lesson

@router.get("/{id}")
async def get_lesson_metadata(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user)
):
    """
    17 GET /api/v1/lessons/{id} - metadata only
    """
    lesson = await get_user_lesson(id, user.id, db)
    
    # Just return basic metadata for now
    return {
        "id": lesson.id,
        "title": lesson.title,
        "objective": lesson.objective,
        "concept_ids": lesson.concept_ids,
        "est_minutes": lesson.est_minutes,
        "status": lesson.status
    }

@router.post("/{id}/start")
@limiter.limit("10/minute")
async def start_lesson(
    id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user)
):
    """
    18 POST /api/v1/lessons/{id}/start - marks in progress, returns thread id
    """
    lesson = await get_user_lesson(id, user.id, db)
        
    if lesson.status == "planned":
        lesson.status = "in_progress"
        await db.commit()
    
    # In a real implementation we might create a TutorThread here
    return {"thread_id": "temp-thread-id"}

async def _stream_lesson_content(lesson_id: UUID, user_id: UUID, db: AsyncSession):
    # Fetch lesson and current profile
    try:
        lesson = await get_user_lesson(lesson_id, user_id, db)
    except NotFoundError as e:
        yield "error", {"code": "NOT_FOUND", "message": "Lesson not found"}
        return
        
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user_id).order_by(LearnerProfile.profile_version.desc()).limit(1)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        yield "error", {"code": "NOT_FOUND", "message": "Profile not found"}
        return

    # Check cache
    cache_result = await db.execute(
        select(LessonContent)
        .where(LessonContent.lesson_id == lesson.id)
        .where(LessonContent.profile_version == profile.profile_version)
    )
    cached_content = cache_result.scalar_one_or_none()

    if cached_content:
        # Cache Hit - stream immediately
        # We simulate streaming the blocks
        blocks = cached_content.blocks.get("blocks", [])
        for block in blocks:
            yield "block", block
            await asyncio.sleep(0.05) # slight artificial delay
            
        yield "done", {
            "message_id": str(cached_content.id),
            "block_count": len(blocks),
            "usage": {"total_tokens": cached_content.token_cost}
        }
        return

    # Cache Miss - call Tutor
    lesson_draft = {
        "title": lesson.title,
        "objective": lesson.objective,
        "concept_ids": lesson.concept_ids,
        "est_minutes": lesson.est_minutes
    }
    
    profile_dict = {
        "prior_knowledge": profile.prior_knowledge,
        "pace": profile.pace.value if profile.pace else None,
        "representation_pref": profile.representation_pref.value if profile.representation_pref else None,
        "scaffolding_pref": profile.scaffolding_pref.value if profile.scaffolding_pref else None,
        "depth_pref": profile.depth_pref.value if profile.depth_pref else None,
        "motivation": profile.motivation.value if profile.motivation else None,
        "session_minutes": profile.session_minutes,
        "language": profile.language,
        "accessibility": profile.accessibility
    }
    
    try:
        gen_task = asyncio.create_task(
            tutor_agent.generate_lesson(
                lesson_draft=lesson_draft,
                profile=profile_dict
            )
        )
        
        stages = ["Reading your profile", "Choosing examples", "Writing the explanation"]
        stage_idx = 0
        
        while not gen_task.done():
            if stage_idx < len(stages):
                yield "tool", {"name": stages[stage_idx], "status": "running"}
                stage_idx += 1
            
            done, _ = await asyncio.wait([gen_task], timeout=2.0)
            if gen_task in done:
                break
                
        draft = gen_task.result()
        
        # We don't have true streaming from the SDK, so we yield blocks one by one
        # as if they were streamed.
        blocks = []
        for block in draft.blocks:
            # Pydantic model dump
            block_dict = block.model_dump()
            blocks.append(block_dict)
            yield "block", block_dict
            # Blocks are generated in one call and replayed here. 
            # We simulate true token streaming with this sleep.
            await asyncio.sleep(0.1)
            
        # Save to DB
        new_content = LessonContent(
            lesson_id=lesson.id,
            profile_version=profile.profile_version,
            blocks={"blocks": blocks},
            token_cost=1500 # hardcoded token cost for now, since usage stats aren't directly available here yet
        )
        db.add(new_content)
        await db.commit()
        await db.refresh(new_content)
        
        yield "done", {
            "message_id": str(new_content.id),
            "block_count": len(blocks),
            "usage": {"total_tokens": new_content.token_cost}
        }
    except Exception as e:
        yield "error", {"code": "INTERNAL_ERROR", "message": str(e), "retryable": True}

@router.get("/{id}/content")
async def stream_lesson_content(
    id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user)
):
    """
    19 GET /api/v1/lessons/{id}/content - SSE stream of ContentBlocks
    """
    return StreamingResponse(
        stream_with_heartbeat(request, _stream_lesson_content(id, user.id, db)),
        media_type="text/event-stream"
    )

async def _stream_reexplain_content(lesson_id: UUID, user_id: UUID, req: ReexplainRequest, db: AsyncSession):
    # Fetch lesson and current profile
    try:
        lesson = await get_user_lesson(lesson_id, user_id, db)
    except NotFoundError as e:
        yield "error", {"code": "NOT_FOUND", "message": "Lesson not found"}
        return
        
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user_id).order_by(LearnerProfile.profile_version.desc()).limit(1)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        yield "error", {"code": "NOT_FOUND", "message": "Profile not found"}
        return

    # Find the original block in lesson content
    cache_result = await db.execute(
        select(LessonContent)
        .where(LessonContent.lesson_id == lesson.id)
        .where(LessonContent.profile_version == profile.profile_version)
    )
    cached_content = cache_result.scalar_one_or_none()
    
    if not cached_content:
        yield "error", {"code": "NOT_FOUND", "message": "Lesson content not found for reexplanation."}
        return
        
    blocks = cached_content.blocks.get("blocks", [])
    original_block = None
    for b in blocks:
        if b.get("id") == str(req.block_id):
            original_block = b
            break
            
    if not original_block:
        yield "error", {"code": "NOT_FOUND", "message": "Block not found."}
        return
        
    # Create confusion_flag signal server-side
    signal = Signal(
        user_id=user_id,
        lesson_id=lesson_id,
        block_id=req.block_id,
        type="confusion_flag",
        value={"reason": req.reason} if req.reason else {}
    )
    db.add(signal)
    await db.commit()
    
    profile_dict = {
        "prior_knowledge": profile.prior_knowledge,
        "pace": profile.pace.value if profile.pace else None,
        "representation_pref": profile.representation_pref.value if profile.representation_pref else None,
        "scaffolding_pref": profile.scaffolding_pref.value if profile.scaffolding_pref else None,
        "depth_pref": profile.depth_pref.value if profile.depth_pref else None,
        "motivation": profile.motivation.value if profile.motivation else None,
        "session_minutes": profile.session_minutes,
        "language": profile.language,
        "accessibility": profile.accessibility
    }
    
    try:
        draft = await tutor_agent.reexplain_block(
            original_block=original_block,
            profile=profile_dict,
            reason=req.reason
        )
        
        reexplain_blocks = []
        for block in draft.blocks:
            block_dict = block.model_dump()
            reexplain_blocks.append(block_dict)
            yield "block", block_dict
            await asyncio.sleep(0.1) # Simulate generation time
            
        yield "done", {
            "message_id": str(uuid.uuid4()),
            "block_count": len(reexplain_blocks),
            "usage": {"total_tokens": 500}, # Mock usage
            "reexplain_strategy": draft.reexplain_strategy
        }
    except Exception as e:
        yield "error", {"code": "INTERNAL_ERROR", "message": str(e), "retryable": True}

@router.post("/{id}/reexplain")
@limiter.limit("5/minute")
async def reexplain_lesson_block(
    id: UUID,
    req: ReexplainRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user)
):
    """
    19b POST /api/v1/lessons/{id}/reexplain - SSE stream
    """
    return StreamingResponse(
        stream_with_heartbeat(request, _stream_reexplain_content(id, user.id, req, db)),
        media_type="text/event-stream"
    )

@router.post("/{id}/complete")
async def complete_lesson(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user)
):
    """
    20 POST /api/v1/lessons/{id}/complete
    """
    lesson = await get_user_lesson(id, user.id, db)
        
    lesson.status = "completed"
    await db.commit()
    
    return {"status": "success"}

@router.post("/{id}/signals", response_model=SignalResponse)
async def create_lesson_signal(
    id: UUID,
    signal_in: SignalCreate,
    db: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user)
):
    """
    25 POST /api/v1/lessons/{id}/signals
    """
    lesson = await get_user_lesson(id, user.id, db)

    new_signal = Signal(
        user_id=user.id,
        lesson_id=lesson.id,
        block_id=signal_in.block_id,
        type=signal_in.type.value,
        value=signal_in.value
    )
    db.add(new_signal)
    await db.commit()
    await db.refresh(new_signal)
    
    return SignalResponse(
        id=new_signal.id,
        user_id=new_signal.user_id,
        lesson_id=new_signal.lesson_id,
        block_id=new_signal.block_id,
        type=new_signal.type,
        value=new_signal.value,
        created_at=new_signal.created_at
    )
