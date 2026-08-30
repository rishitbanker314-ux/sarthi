import uuid
from typing import Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

from services.api.models.enums import AdaptationTrigger, SignalType
from services.api.models.adaptation import AdaptationEvent
from services.api.models.lesson_execution import CheckpointAttempt, Checkpoint, Signal
from services.api.models.planner import Lesson
from services.api.adaptation import config

class TriggerResult(BaseModel):
    trigger: AdaptationTrigger

async def evaluate(user_id: uuid.UUID, lesson_id: Optional[uuid.UUID], db: AsyncSession) -> Optional[TriggerResult]:
    """
    Evaluate deterministic triggers to decide if an adaptation is needed.
    Returns the highest-priority triggered action, or None if no triggers fire.
    """
    now = datetime.now(timezone.utc)

    # 1. Check cooldowns (do not fire same trigger twice in COOLDOWN_MINUTES)
    # AND handle declined adaptations (do not re-prompt same trigger within 24 hours)
    cooldown_cutoff = now - timedelta(minutes=config.COOLDOWN_MINUTES)
    decline_cutoff = now - timedelta(hours=24)
    
    stmt = select(AdaptationEvent.trigger, AdaptationEvent.accepted, AdaptationEvent.created_at).where(
        AdaptationEvent.user_id == user_id,
        AdaptationEvent.created_at > decline_cutoff
    )
    result = await db.execute(stmt)
    
    recent_triggers = set()
    for row in result.all():
        trigger, accepted, created_at = row
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
            
        # Standard cooldown (any state)
        if created_at > cooldown_cutoff:
            recent_triggers.add(trigger)
            
        # Declined cooldown
        if accepted is False and created_at > decline_cutoff:
            recent_triggers.add(trigger)

    # 2. Fetch checkpoint scores if we have a lesson_id
    scores = []
    if lesson_id:
        stmt = (
            select(CheckpointAttempt.score)
            .join(Checkpoint, CheckpointAttempt.checkpoint_id == Checkpoint.id)
            .where(Checkpoint.user_id == user_id, Checkpoint.lesson_id == lesson_id)
            .order_by(desc(CheckpointAttempt.created_at))
            .limit(max(config.STRUGGLING_CONSECUTIVE_COUNT, config.RACING_CONSECUTIVE_COUNT))
        )
        result = await db.execute(stmt)
        scores = [float(row[0]) for row in result.all()]

    # TRIGGER 1: Struggling
    if AdaptationTrigger.struggling not in recent_triggers and scores:
        if scores[0] < config.STRUGGLING_SCORE_THRESHOLD:
            return TriggerResult(trigger=AdaptationTrigger.struggling)
        if len(scores) >= config.STRUGGLING_CONSECUTIVE_COUNT and all(s < config.STRUGGLING_CONSECUTIVE_THRESHOLD for s in scores[:config.STRUGGLING_CONSECUTIVE_COUNT]):
            return TriggerResult(trigger=AdaptationTrigger.struggling)

    # TRIGGER 2: Stuck
    if lesson_id and AdaptationTrigger.stuck not in recent_triggers:
        stmt = select(func.count(Signal.id)).where(
            Signal.user_id == user_id,
            Signal.lesson_id == lesson_id,
            Signal.type == SignalType.confusion_flag
        )
        confusion_count = (await db.execute(stmt)).scalar_one()
        if confusion_count >= config.STUCK_CONFUSION_COUNT:
            return TriggerResult(trigger=AdaptationTrigger.stuck)

    # TRIGGER 3: Racing
    if lesson_id and AdaptationTrigger.racing not in recent_triggers and len(scores) >= config.RACING_CONSECUTIVE_COUNT:
        if all(s > config.RACING_SCORE_THRESHOLD for s in scores[:config.RACING_CONSECUTIVE_COUNT]):
            stmt = select(Lesson.est_minutes).where(Lesson.id == lesson_id)
            est_minutes = (await db.execute(stmt)).scalar_one_or_none()
            if est_minutes:
                stmt = select(Signal.value).where(
                    Signal.user_id == user_id,
                    Signal.lesson_id == lesson_id,
                    Signal.type == SignalType.time_on_block
                )
                time_signals = (await db.execute(stmt)).scalars().all()
                elapsed_seconds = sum(float(sig.get('time', 0)) for sig in time_signals)
                elapsed_minutes = elapsed_seconds / 60.0
                if elapsed_minutes < (est_minutes * config.RACING_TIME_RATIO):
                    return TriggerResult(trigger=AdaptationTrigger.racing)

    # TRIGGER 4: Stalled
    if AdaptationTrigger.stalled not in recent_triggers:
        stmt = select(Signal.created_at).where(Signal.user_id == user_id).order_by(desc(Signal.created_at)).limit(1)
        last_signal = (await db.execute(stmt)).scalar_one_or_none()
        # Ensure last_signal has timezone for comparison
        if last_signal:
            if last_signal.tzinfo is None:
                last_signal = last_signal.replace(tzinfo=timezone.utc)
            if (now - last_signal) >= timedelta(days=config.STALLED_DAYS):
                return TriggerResult(trigger=AdaptationTrigger.stalled)
        else:
            # If no signals ever, are they stalled? Let's say yes, if the user account is older than 3 days.
            # But the prompt says "no signals row for this learner in >= 3 days". 
            # We can check user created_at, but we'll assume no signals means stalled.
            # Let's query user created_at to be safe.
            from services.api.models.user import User
            stmt_u = select(User.created_at).where(User.id == user_id)
            user_created = (await db.execute(stmt_u)).scalar_one_or_none()
            if user_created:
                if user_created.tzinfo is None:
                    user_created = user_created.replace(tzinfo=timezone.utc)
                if (now - user_created) >= timedelta(days=config.STALLED_DAYS):
                    return TriggerResult(trigger=AdaptationTrigger.stalled)

    # TRIGGER 5: Decaying
    # NOT WIRED IN V1 — depends on S4 spaced repetition.

    return None
