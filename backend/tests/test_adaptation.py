import pytest
import uuid
import contextlib
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, timedelta

from services.api.models.planner import Plan, Module, Lesson, Goal
from services.api.models.lesson_execution import Checkpoint, CheckpointAttempt, LessonContent
from services.api.models.adaptation import AdaptationEvent
from services.api.models.enums import AdaptationTrigger, AdaptationAction
from services.api.jobs.replan import run_replan

@contextlib.asynccontextmanager
async def mock_session_maker(session):
    yield session

@pytest.mark.asyncio
async def test_replan_struggling_flow(db_session: AsyncSession, test_user, client: AsyncClient, token_headers: dict, monkeypatch):
    import services.api.jobs.replan as replan_module
    monkeypatch.setattr(replan_module, "async_session", lambda: mock_session_maker(db_session))
    
    from services.api.models.learner_profile import LearnerProfile
    from services.api.models.enums import Pace, RepresentationPref, ScaffoldingPref, DepthPref, Motivation
    profile = LearnerProfile(
        user_id=test_user.id, 
        profile_version=1,
        pace=Pace.standard,
        representation_pref=RepresentationPref.concrete_first,
        scaffolding_pref=ScaffoldingPref.worked_examples,
        depth_pref=DepthPref.breadth_survey,
        motivation=Motivation.career,
        session_minutes=30,
        language="en"
    )
    db_session.add(profile)
    
    # 1. Setup Goal, Plan, Module, Lesson
    goal = Goal(user_id=test_user.id, raw_input="Learn Python", normalized_topic="Python", target_level="beginner", status="active")
    db_session.add(goal)
    await db_session.flush()
    
    plan = Plan(goal_id=goal.id, version=1, title="Python Plan", rationale="Learn it", profile_version=1, status="active")
    db_session.add(plan)
    await db_session.flush()
    
    module = Module(plan_id=plan.id, title="Basics", objective="Learn basic syntax", rationale="Start somewhere", order_index=0, est_minutes=15, status="not_started")
    db_session.add(module)
    await db_session.flush()
    
    lesson = Lesson(module_id=module.id, title="Intro", objective="Hello world", order_index=0, concept_ids=[], est_minutes=15, status="not_started")
    db_session.add(lesson)
    await db_session.flush()
    
    content = LessonContent(lesson_id=lesson.id, profile_version=1, blocks=[], token_cost=100)
    db_session.add(content)
    await db_session.flush()
    
    # 2. Add struggling signal
    cp = Checkpoint(user_id=test_user.id, lesson_id=lesson.id, items={})
    db_session.add(cp)
    await db_session.flush()
    
    cpa = CheckpointAttempt(checkpoint_id=cp.id, responses={}, score=0.4, mastery_deltas={}, feedback={})
    db_session.add(cpa)
    await db_session.commit()
    
    # 3. Mock AdaptorAgent
    from services.agents.schemas import AdaptationDecision
    async def mock_generate_decision(*args, **kwargs):
        return AdaptationDecision(
            trigger="struggling",
            action="reexplain_concept",
            reason="The learner is having trouble with syntax based on recent scores, resulting in low comprehension.",
            timeline_impact="adds ~5 mins to lesson timeline",
            changes=[]
        )
    
    monkeypatch.setattr("services.api.jobs.replan.AdaptorAgent.generate_decision", mock_generate_decision)
    
    async def dummy_report(prog, msg):
        pass
    
    result = await run_replan(plan.id, test_user.id, dummy_report, lesson.id)
    assert result is not None
    assert result.plan_id != plan.id
    
    # Check new plan
    new_plan = (await db_session.execute(select(Plan).where(Plan.id == result.plan_id))).scalar_one()
    assert new_plan.version == 2
    assert new_plan.status == "draft"
    
    # Check adaptation event
    event = (await db_session.execute(select(AdaptationEvent).where(AdaptationEvent.id == result.adaptation_event_id))).scalar_one()
    assert event.trigger == AdaptationTrigger.struggling
    assert event.accepted is None
    
    # 4. GET /adaptations
    resp = await client.get("/api/v1/adaptations", headers=token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == str(event.id)
    
    # 5. POST /adaptations/{id}/respond (Decline first)
    resp = await client.post(f"/api/v1/adaptations/{event.id}/respond", json={"accepted": False}, headers=token_headers)
    assert resp.status_code == 200
    
    await db_session.refresh(event)
    assert event.accepted is False
    
    await db_session.refresh(new_plan)
    assert new_plan.status == "draft" # Not activated
    await db_session.refresh(plan)
    assert plan.status == "active" # Old plan still active
    
    # 6. Verify cooldown works
    # If we run replan again right now, it should return None because of decline cooldown
    result2 = await run_replan(plan.id, test_user.id, dummy_report)
    # The dummy replan returns a result anyway if NO triggers hit because of the check
    # Wait, in run_replan: if not trigger_result: return ReplanResult(...)
    # It returns a dummy one if no triggers hit. Let's assert it did hit the no-triggers path by checking no NEW events created
    # Actually wait: event id will be newly generated in run_replan but not saved. Let's check DB.
    events_count = (await db_session.execute(select(AdaptationEvent))).scalars().all()
    assert len(events_count) == 1 # No new event saved
    
    # Let's artificially move the first event's created_at to 25 hours ago to bypass cooldown
    event.created_at = datetime.now(timezone.utc) - timedelta(hours=25)
    await db_session.commit()
    
    # Run again - should generate new event
    result3 = await run_replan(plan.id, test_user.id, dummy_report, lesson.id)
    events_count_new = (await db_session.execute(select(AdaptationEvent))).scalars().all()
    assert len(events_count_new) == 2
    event3 = [e for e in events_count_new if e.id == result3.adaptation_event_id][0]
    
    # Accept the new adaptation
    resp = await client.post(f"/api/v1/adaptations/{event3.id}/respond", json={"accepted": True}, headers=token_headers)
    assert resp.status_code == 200
    
    await db_session.refresh(plan)
    assert plan.status == "inactive" # Old plan deactivated
    
    new_plan3 = (await db_session.execute(select(Plan).where(Plan.id == result3.plan_id))).scalar_one()
    assert new_plan3.status == "active" # New plan activated
