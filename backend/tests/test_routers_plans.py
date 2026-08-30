import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import pytest_asyncio

from services.api.models.planner import Goal, Plan, Job
from services.api.models.enums import JobKind, JobStatus
from services.api.models.learner_profile import LearnerProfile

@pytest_asyncio.fixture
async def goal(db_session: AsyncSession, test_user):
    goal_id = uuid.uuid4()
    goal = Goal(
        id=goal_id,
        user_id=test_user.id,
        raw_input="Learn python",
        normalized_topic="Python",
        target_level="Beginner",
        status="captured",
        is_educational=True
    )
    db_session.add(goal)
    await db_session.commit()
    return goal

@pytest_asyncio.fixture
async def profile(db_session: AsyncSession, test_user):
    prof = LearnerProfile(
        user_id=test_user.id,
        profile_version=1,
        prior_knowledge={"general": "shaky"},
        pace="standard",
        representation_pref="concrete_first",
        scaffolding_pref="worked_examples",
        depth_pref="breadth_survey",
        motivation="curiosity",
        session_minutes=30,
        language="en",
        accessibility={}
    )
    db_session.add(prof)
    await db_session.commit()
    return prof

class DummySessionMaker:
    def __init__(self, session):
        self.session = session
    def __call__(self):
        return self
    async def __aenter__(self):
        return self.session
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.mark.asyncio
async def test_plan_generation_flow(client: AsyncClient, db_session: AsyncSession, test_user, goal, profile, token_headers, monkeypatch):
    # Patch the session maker so the background task uses the transactional session
    monkeypatch.setattr("services.api.jobs.runner.async_session", DummySessionMaker(db_session))
    monkeypatch.setattr("services.api.jobs.plan_generation.async_session", DummySessionMaker(db_session))
    
    # 1. Trigger Plan Generation
    response = await client.post(
        f"/api/v1/goals/{goal.id}/plan",
        headers=token_headers
    )
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    job_id = data["job_id"]
    
    # 2. Wait for Job to Complete
    import asyncio
    max_retries = 30
    for _ in range(max_retries):
        job_resp = await client.get(f"/api/v1/jobs/{job_id}", headers=token_headers)
        assert job_resp.status_code == 200
        job_data = job_resp.json()
        if job_data["status"] == "succeeded":
            assert "result" in job_data and job_data["result"] is not None, "Job result is missing"
            assert "plan_id" in job_data["result"], "plan_id missing from job result"
            assert job_data["result"]["plan_id"] is not None
            break
        elif job_data["status"] == "failed":
            pytest.fail(f"Job failed: {job_data.get('error')}")
        await asyncio.sleep(0.1)
    else:
        pytest.fail("Job did not complete in time")
        
    # 3. Verify Plan was Persisted
    plan_result = await db_session.execute(select(Plan).where(Plan.goal_id == goal.id))
    plan = plan_result.scalar_one_or_none()
    assert plan is not None
    assert plan.profile_version == profile.profile_version
    
    # 4. Test GET /api/v1/plans/{id}
    # Track query count with SQLAlchemy Events
    from sqlalchemy import event
    query_count = 0
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        nonlocal query_count
        query_count += 1
        
    event.listen(db_session.bind.sync_engine, "before_cursor_execute", before_cursor_execute)
    try:
        plan_resp = await client.get(f"/api/v1/plans/{plan.id}", headers=token_headers)
        assert plan_resp.status_code == 200
        plan_data = plan_resp.json()
        assert plan_data["id"] == str(plan.id)
        assert len(plan_data["modules"]) >= 3
        assert len(plan_data["modules"][0]["lessons"]) >= 2
        
        # Verify query count is under 5
        assert query_count < 5, f"Query count was {query_count}, expected < 5 (eager loading broken)"
    finally:
        event.remove(db_session.bind.sync_engine, "before_cursor_execute", before_cursor_execute)


@pytest.mark.asyncio
async def test_plan_already_generating_guard(client: AsyncClient, db_session: AsyncSession, test_user, goal, profile, token_headers):
    # Setup a running job
    job = Job(
        user_id=test_user.id,
        kind=JobKind.plan_generation,
        status=JobStatus.running
    )
    db_session.add(job)
    await db_session.commit()
    
    # Try to generate again
    response = await client.post(
        f"/api/v1/goals/{goal.id}/plan",
        headers=token_headers
    )
    assert response.status_code == 409
    data = response.json()
    assert "PLAN_ALREADY_GENERATING" in data["error"]["message"]
