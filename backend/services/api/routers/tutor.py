from typing import Any, List
import asyncio
import uuid
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from services.api.db import get_session
from services.api.auth.dependencies import get_current_user, CurrentUser
from services.api.errors import AppError, NotFoundError
from services.api.models import Lesson, TutorThread, TutorMessage, LearnerProfile, LessonContent
from services.api.models.enums import MessageRole
from services.api.schemas.tutor import TutorMessageRequest, TutorThreadResponse
from services.agents.tutor import TutorAgent
from services.api.sse import stream_with_heartbeat
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/tutor", tags=["tutor"])
tutor_agent = TutorAgent()

async def _stream_tutor_reply(user_id: UUID, req: TutorMessageRequest, db: AsyncSession):
    # Fetch thread or create new
    if req.thread_id:
        thread = await db.get(TutorThread, req.thread_id)
        if not thread:
            yield "error", {"code": "NOT_FOUND", "message": "Thread not found"}
            return
    else:
        thread = TutorThread(user_id=user_id, lesson_id=req.lesson_id)
        db.add(thread)
        await db.commit()
        await db.refresh(thread)
        
    # Save user message
    user_msg = TutorMessage(
        thread_id=thread.id,
        role=MessageRole.user,
        content=req.content
    )
    db.add(user_msg)
    await db.commit()
    
    # Fetch conversation history
    messages_result = await db.execute(
        select(TutorMessage).where(TutorMessage.thread_id == thread.id).order_by(TutorMessage.created_at)
    )
    history = [{"role": m.role.name, "content": m.content} for m in messages_result.scalars().all()]
    
    # Fetch learner profile
    profile_result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user_id).order_by(LearnerProfile.profile_version.desc()).limit(1)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        yield "error", {"code": "NOT_FOUND", "message": "Profile not found"}
        return
        
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
    
    # Fetch context block if provided
    context_block = None
    if req.context_block_id:
        content_result = await db.execute(
            select(LessonContent)
            .where(LessonContent.lesson_id == req.lesson_id)
            .where(LessonContent.profile_version == profile.profile_version)
        )
        content_doc = content_result.scalar_one_or_none()
        if content_doc:
            for b in content_doc.blocks.get("blocks", []):
                if b.get("id") == str(req.context_block_id):
                    context_block = b
                    break
    
    try:
        draft = await tutor_agent.chat_reply(
            message=req.content,
            history=history,
            profile=profile_dict,
            context_block=context_block
        )
        
        # Save tutor message
        tutor_msg = TutorMessage(
            thread_id=thread.id,
            role=MessageRole.assistant,
            content=draft.message,
            blocks={"blocks": [b.model_dump() for b in draft.blocks]} if draft.blocks else None
        )
        db.add(tutor_msg)
        await db.commit()
        await db.refresh(tutor_msg)
        
        # Stream response
        # Stream prose as 'token' events. We simulate tokens by splitting by space.
        words = draft.message.split(' ')
        for i, word in enumerate(words):
            yield "token", {"text": word + (" " if i < len(words) - 1 else "")}
            await asyncio.sleep(0.01)
            
        # Stream blocks
        if draft.blocks:
            for block in draft.blocks:
                yield "block", block.model_dump()
                await asyncio.sleep(0.05)
                
        yield "done", {
            "message_id": str(tutor_msg.id),
            "thread_id": str(thread.id),
            "block_count": len(draft.blocks),
            "usage": {"total_tokens": 150} # mock usage
        }
    except Exception as e:
        yield "error", {"code": "INTERNAL_ERROR", "message": str(e), "retryable": True}

@router.post("/messages")
async def send_tutor_message(
    req: TutorMessageRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user)
):
    """
    21 POST /api/v1/tutor/messages - SSE stream
    """
    return StreamingResponse(
        stream_with_heartbeat(request, _stream_tutor_reply(user.id, req, db)),
        media_type="text/event-stream"
    )

@router.get("/threads/{id}")
async def get_tutor_thread(
    id: UUID,
    db: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user)
):
    """
    22 GET /api/v1/tutor/threads/{id}
    """
    thread = await db.execute(
        select(TutorThread).options(selectinload(TutorThread.messages)).where(TutorThread.id == id)
    )
    thread_obj = thread.scalar_one_or_none()
    
    if not thread_obj:
        raise NotFoundError("Thread not found")
        
    return TutorThreadResponse(
        id=thread_obj.id,
        lesson_id=thread_obj.lesson_id,
        messages=[
            {
                "id": m.id,
                "thread_id": m.thread_id,
                "role": m.role,
                "content": m.content,
                "blocks": m.blocks,
                "created_at": m.created_at
            }
            for m in thread_obj.messages
        ]
    )
