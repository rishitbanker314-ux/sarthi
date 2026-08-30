import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_create_signal(client: AsyncClient, db_session, test_user, token_headers):
    # Setup Lesson
    from services.api.models import Goal, Plan, Module, Lesson, Concept
    goal = Goal(id=uuid.uuid4(), user_id=test_user.id, raw_input="t", normalized_topic="t", target_level="t", status="active")
    db_session.add(goal)
    plan = Plan(id=uuid.uuid4(), goal_id=goal.id, version=1, title="t", rationale="t", profile_version=1, status="active")
    db_session.add(plan)
    module = Module(id=uuid.uuid4(), plan_id=plan.id, order_index=0, title="t", objective="t", rationale="t", est_minutes=5, status="active")
    db_session.add(module)
    concept = Concept(id=uuid.uuid4(), name="T", description="T", domain="T")
    db_session.add(concept)
    lesson = Lesson(id=uuid.uuid4(), module_id=module.id, order_index=0, title="T", objective="T", concept_ids=[concept.id], est_minutes=5, status="planned")
    db_session.add(lesson)
    await db_session.commit()

    # Create signal
    block_id = str(uuid.uuid4())
    resp = await client.post(f"/api/v1/lessons/{lesson.id}/signals", json={
        "type": "time_on_block",
        "block_id": block_id,
        "value": {"seconds": 42}
    }, headers=token_headers)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["type"] == "time_on_block"
    assert data["value"]["seconds"] == 42
    assert data["lesson_id"] == str(lesson.id)

@pytest.mark.asyncio
async def test_get_signals(client: AsyncClient, db_session, test_user, token_headers):
    # Setup Signal
    from services.api.models import Signal
    signal = Signal(user_id=test_user.id, type="skip", value={"reason": "too easy"})
    db_session.add(signal)
    await db_session.commit()

    resp = await client.get("/api/v1/users/me/signals", headers=token_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["type"] == "skip"
    assert data[0]["value"]["reason"] == "too easy"

@pytest.mark.asyncio
async def test_get_progress(client: AsyncClient, db_session, test_user, token_headers):
    # Setup MasteryState
    from services.api.models import MasteryState, Concept
    concept = Concept(id=uuid.uuid4(), name="C", description="C", domain="C")
    db_session.add(concept)
    mastery = MasteryState(
        user_id=test_user.id,
        concept_id=concept.id,
        score=0.85,
        confidence=0.9,
        attempts=3
    )
    db_session.add(mastery)
    await db_session.commit()

    resp = await client.get("/api/v1/users/me/progress", headers=token_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["score"] == "0.85"
    assert data[0]["concept_id"] == str(concept.id)
