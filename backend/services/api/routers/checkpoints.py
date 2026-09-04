from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from uuid import UUID
import uuid

from services.api.db import get_session
from services.api.auth.dependencies import get_current_user
from services.api.models import User, Lesson, LearnerProfile, Signal, Checkpoint, CheckpointAttempt, MasteryState
from services.api.models.enums import SignalType
from services.api.schemas.checkpoint import CheckpointResponse, CheckpointSubmitRequest, CheckpointAttemptResponse, CheckpointItem, ItemFeedback
from services.agents.assessor import AssessorAgent

router = APIRouter(tags=["Checkpoints"])

@router.post("/api/v1/lessons/{lesson_id}/checkpoint", response_model=CheckpointResponse)
async def generate_checkpoint(
    lesson_id: UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    lesson_result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    profile_result = await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Fetch recent signals
    signals_result = await db.execute(
        select(Signal).where(Signal.user_id == user.id).order_by(Signal.created_at.desc()).limit(10)
    )
    signals = signals_result.scalars().all()
    signals_data = [{"type": s.type, "data": s.value, "created_at": s.created_at.isoformat()} for s in signals]

    lesson_data = {
        "title": lesson.title,
        "objective": lesson.objective,
        "concept_ids": [str(c) for c in lesson.concept_ids]
    }

    profile_data = {
        "profile_version": profile.profile_version,
        "prior_knowledge": profile.prior_knowledge,
        "pace": profile.pace.value if hasattr(profile.pace, 'value') else profile.pace,
        "representation_pref": profile.representation_pref.value if hasattr(profile.representation_pref, 'value') else profile.representation_pref,
        "scaffolding_pref": profile.scaffolding_pref.value if hasattr(profile.scaffolding_pref, 'value') else profile.scaffolding_pref,
        "depth_pref": profile.depth_pref.value if hasattr(profile.depth_pref, 'value') else profile.depth_pref,
        "motivation": profile.motivation.value if hasattr(profile.motivation, 'value') else profile.motivation,
        "session_minutes": profile.session_minutes,
        "language": profile.language,
        "accessibility": profile.accessibility
    }

    agent = AssessorAgent()
    draft = await agent.generate_checkpoint(lesson_data, profile_data, signals_data)

    items_data = [item.model_dump(mode='json') for item in draft.items]
    
    checkpoint = Checkpoint(
        lesson_id=lesson.id,
        user_id=user.id,
        items={"items": items_data}
    )
    db.add(checkpoint)
    await db.commit()
    await db.refresh(checkpoint)

    return CheckpointResponse(
        id=checkpoint.id,
        lesson_id=checkpoint.lesson_id,
        items=[CheckpointItem(**item) for item in items_data],
        created_at=checkpoint.created_at
    )


@router.post("/api/v1/checkpoints/{checkpoint_id}/submit", response_model=CheckpointAttemptResponse)
async def submit_checkpoint(
    checkpoint_id: UUID,
    req: CheckpointSubmitRequest,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    checkpoint_result = await db.execute(select(Checkpoint).where(Checkpoint.id == checkpoint_id))
    checkpoint = checkpoint_result.scalar_one_or_none()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    agent = AssessorAgent()
    evaluation = await agent.evaluate_checkpoint(checkpoint.items.get("items", []), req.responses)

    attempt = CheckpointAttempt(
        checkpoint_id=checkpoint.id,
        responses={"responses": req.responses},
        score=evaluation.score,
        mastery_deltas={"deltas": [d.model_dump(mode='json') for d in evaluation.mastery_deltas]},
        feedback={"feedback": [f.model_dump(mode='json') for f in evaluation.feedback]}
    )
    db.add(attempt)

    # Log signal
    signal = Signal(
        user_id=user.id,
        type=SignalType.checkpoint_score,
        value={
            "checkpoint_id": str(checkpoint.id),
            "lesson_id": str(checkpoint.lesson_id),
            "score": float(evaluation.score)
        }
    )
    db.add(signal)

    # Update MasteryState
    mastery_deltas_resp = []
    for delta in evaluation.mastery_deltas:
        mastery_result = await db.execute(
            select(MasteryState).where(
                MasteryState.user_id == user.id,
                MasteryState.concept_id == delta.concept_id
            )
        )
        mastery = mastery_result.scalar_one_or_none()
        if mastery:
            mastery.score = min(1.0, max(0.0, float(mastery.score) + delta.delta))
            mastery.attempts += 1
        else:
            # Create new
            mastery = MasteryState(
                user_id=user.id,
                concept_id=delta.concept_id,
                score=min(1.0, max(0.0, 0.5 + delta.delta)), # Base mastery 0.5?
                confidence=0.5,
                attempts=1
            )
            db.add(mastery)
        
        mastery_deltas_resp.append({
            "concept_id": delta.concept_id,
            "delta": delta.delta
        })

    await db.commit()
    await db.refresh(attempt)

    return CheckpointAttemptResponse(
        id=attempt.id,
        score=attempt.score,
        mastery_deltas=mastery_deltas_resp,
        feedback=[ItemFeedback(**f.model_dump()) for f in evaluation.feedback],
        submitted_at=attempt.created_at
    )
