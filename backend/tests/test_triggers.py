import pytest
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.api.models import User, Goal, Plan, Module, Lesson, Checkpoint, CheckpointAttempt, Signal
from services.api.models.enums import AdaptationTrigger, SignalType
from services.api.models.adaptation import AdaptationEvent
from services.api.adaptation.triggers import evaluate

import pytest_asyncio

@pytest_asyncio.fixture
async def setup_data(db_session: AsyncSession):
    user_id = uuid.uuid4()
    user = User(id=user_id, email="test@test.com", display_name="Test")
    db_session.add(user)
    await db_session.flush()

    goal = Goal(id=uuid.uuid4(), user_id=user.id, raw_input="t", normalized_topic="t", target_level="t", status="active")
    db_session.add(goal)
    plan = Plan(id=uuid.uuid4(), goal_id=goal.id, version=1, title="t", rationale="t", profile_version=1, status="active")
    db_session.add(plan)
    module = Module(id=uuid.uuid4(), plan_id=plan.id, order_index=0, title="t", objective="t", rationale="t", est_minutes=5, status="active")
    db_session.add(module)
    
    lesson = Lesson(
        module_id=module.id,
        order_index=1,
        title="Test Lesson",
        objective="Testing triggers",
        concept_ids=[],
        est_minutes=10,
        status="active"
    )
    db_session.add(lesson)
    
    plan2 = Plan(id=uuid.uuid4(), goal_id=goal.id, version=2, title="t2", rationale="t2", profile_version=1, status="active")
    db_session.add(plan2)
    
    await db_session.commit()

    return {"user": user, "lesson": lesson, "plan": plan}

@pytest.mark.asyncio
async def test_evaluate_struggling_single_low(db_session: AsyncSession, setup_data):
    user = setup_data["user"]
    lesson = setup_data["lesson"]

    checkpoint = Checkpoint(lesson_id=lesson.id, user_id=user.id, items={})
    db_session.add(checkpoint)
    await db_session.flush()

    attempt = CheckpointAttempt(
        checkpoint_id=checkpoint.id,
        responses={},
        score=0.4,
        mastery_deltas={},
        feedback={}
    )
    db_session.add(attempt)
    await db_session.commit()

    result = await evaluate(user.id, lesson.id, db_session)
    assert result is not None
    assert result.trigger == AdaptationTrigger.struggling

@pytest.mark.asyncio
async def test_evaluate_struggling_consecutive(db_session: AsyncSession, setup_data):
    user = setup_data["user"]
    lesson = setup_data["lesson"]

    checkpoint = Checkpoint(lesson_id=lesson.id, user_id=user.id, items={})
    db_session.add(checkpoint)
    await db_session.flush()

    # Two consecutive < 0.7
    for score in [0.65, 0.65]:
        attempt = CheckpointAttempt(
            checkpoint_id=checkpoint.id,
            responses={},
            score=score,
            mastery_deltas={},
            feedback={}
        )
        db_session.add(attempt)
    await db_session.commit()

    result = await evaluate(user.id, lesson.id, db_session)
    assert result is not None
    assert result.trigger == AdaptationTrigger.struggling

@pytest.mark.asyncio
async def test_evaluate_struggling_negative(db_session: AsyncSession, setup_data):
    user = setup_data["user"]
    lesson = setup_data["lesson"]

    checkpoint = Checkpoint(lesson_id=lesson.id, user_id=user.id, items={})
    db_session.add(checkpoint)
    await db_session.flush()

    attempt = CheckpointAttempt(
        checkpoint_id=checkpoint.id,
        responses={},
        score=0.8,
        mastery_deltas={},
        feedback={}
    )
    db_session.add(attempt)
    await db_session.commit()

    result = await evaluate(user.id, lesson.id, db_session)
    assert result is None or result.trigger != AdaptationTrigger.struggling

@pytest.mark.asyncio
async def test_evaluate_stuck(db_session: AsyncSession, setup_data):
    user = setup_data["user"]
    lesson = setup_data["lesson"]

    for _ in range(2):
        sig = Signal(user_id=user.id, lesson_id=lesson.id, type=SignalType.confusion_flag, value={})
        db_session.add(sig)
    await db_session.commit()

    result = await evaluate(user.id, lesson.id, db_session)
    assert result is not None
    assert result.trigger == AdaptationTrigger.stuck

@pytest.mark.asyncio
async def test_evaluate_stuck_negative(db_session: AsyncSession, setup_data):
    user = setup_data["user"]
    lesson = setup_data["lesson"]

    sig = Signal(user_id=user.id, lesson_id=lesson.id, type=SignalType.confusion_flag, value={})
    db_session.add(sig)
    await db_session.commit()

    result = await evaluate(user.id, lesson.id, db_session)
    assert result is None or result.trigger != AdaptationTrigger.stuck

@pytest.mark.asyncio
async def test_evaluate_racing(db_session: AsyncSession, setup_data):
    user = setup_data["user"]
    lesson = setup_data["lesson"]
    # est_minutes = 10, RACING_TIME_RATIO = 0.6 -> < 6 mins (360 seconds)

    checkpoint = Checkpoint(lesson_id=lesson.id, user_id=user.id, items={})
    db_session.add(checkpoint)
    await db_session.flush()

    for score in [0.95, 0.95]:
        attempt = CheckpointAttempt(
            checkpoint_id=checkpoint.id,
            responses={},
            score=score,
            mastery_deltas={},
            feedback={}
        )
        db_session.add(attempt)

    sig = Signal(user_id=user.id, lesson_id=lesson.id, type=SignalType.time_on_block, value={"time": 300}) # 5 mins
    db_session.add(sig)
    await db_session.commit()

    result = await evaluate(user.id, lesson.id, db_session)
    assert result is not None
    assert result.trigger == AdaptationTrigger.racing

@pytest.mark.asyncio
async def test_evaluate_racing_negative_time(db_session: AsyncSession, setup_data):
    user = setup_data["user"]
    lesson = setup_data["lesson"]

    checkpoint = Checkpoint(lesson_id=lesson.id, user_id=user.id, items={})
    db_session.add(checkpoint)
    await db_session.flush()

    for score in [0.95, 0.95]:
        attempt = CheckpointAttempt(
            checkpoint_id=checkpoint.id,
            responses={},
            score=score,
            mastery_deltas={},
            feedback={}
        )
        db_session.add(attempt)

    sig = Signal(user_id=user.id, lesson_id=lesson.id, type=SignalType.time_on_block, value={"time": 600}) # 10 mins
    db_session.add(sig)
    await db_session.commit()

    result = await evaluate(user.id, lesson.id, db_session)
    assert result is None or result.trigger != AdaptationTrigger.racing

@pytest.mark.asyncio
async def test_evaluate_stalled(db_session: AsyncSession, setup_data):
    user = setup_data["user"]
    
    sig = Signal(user_id=user.id, type=SignalType.session_abandon, value={}, created_at=datetime.now(timezone.utc) - timedelta(days=4))
    db_session.add(sig)
    await db_session.commit()

    result = await evaluate(user.id, None, db_session)
    assert result is not None
    assert result.trigger == AdaptationTrigger.stalled

@pytest.mark.asyncio
async def test_evaluate_stalled_negative(db_session: AsyncSession, setup_data):
    user = setup_data["user"]
    
    sig = Signal(user_id=user.id, type=SignalType.session_abandon, value={}, created_at=datetime.now(timezone.utc) - timedelta(days=1))
    db_session.add(sig)
    await db_session.commit()

    result = await evaluate(user.id, None, db_session)
    assert result is None

@pytest.mark.asyncio
async def test_evaluate_cooldown(db_session: AsyncSession, setup_data):
    user = setup_data["user"]
    lesson = setup_data["lesson"]

    # Trigger struggling condition
    checkpoint = Checkpoint(lesson_id=lesson.id, user_id=user.id, items={})
    db_session.add(checkpoint)
    await db_session.flush()

    attempt = CheckpointAttempt(
        checkpoint_id=checkpoint.id,
        responses={},
        score=0.4,
        mastery_deltas={},
        feedback={}
    )
    db_session.add(attempt)
    
    # Record that struggling fired 5 mins ago
    event = AdaptationEvent(
        user_id=user.id,
        plan_id=setup_data["plan"].id, # Mock relation
        trigger=AdaptationTrigger.struggling,
        action="no_op",
        reason="test",
        timeline_impact="test",
        before={},
        after={},
        created_at=datetime.now(timezone.utc) - timedelta(minutes=5)
    )
    db_session.add(event)
    await db_session.commit()

    # Even though score < 0.5, the cooldown should prevent it
    result = await evaluate(user.id, lesson.id, db_session)
    assert result is None or result.trigger != AdaptationTrigger.struggling
