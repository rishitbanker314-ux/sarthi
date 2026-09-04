import pytest
import asyncio
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import BackgroundTasks

from services.api.models.planner import Job
from services.api.models.enums import JobKind, JobStatus
from services.api.jobs.runner import dispatch
from services.api.errors import AppError
from services.api.schemas.job import PlanGenerationResult
import contextlib

@contextlib.asynccontextmanager
async def mock_session_maker(session):
    yield session


async def mock_success_work(report):
    await report(10, "Started")
    await asyncio.sleep(0.1)
    await report(50, "Halfway")
    await asyncio.sleep(0.1)
    await report(90, "Almost done")
    return PlanGenerationResult(plan_id=uuid.uuid4())

async def mock_timeout_work(report):
    await report(10, "Started but will timeout")
    await asyncio.sleep(200) # This will timeout
    return None

async def mock_app_error_work(report):
    await report(10, "Started but will error")
    raise AppError(code="TEST_ERROR", message="Test error occurred", retryable=False, details={"foo": "bar"}, http_status=400)

async def mock_unhandled_error_work(report):
    await report(10, "Started but will crash")
    raise ValueError("Crash")

@pytest.fixture
def background_tasks():
    return BackgroundTasks()

@pytest.mark.asyncio
async def test_job_dispatch_and_success(db_session: AsyncSession, test_user, background_tasks, monkeypatch):
    import services.api.jobs.runner as runner
    monkeypatch.setattr(runner, "async_session", lambda: mock_session_maker(db_session))
    
    # Dispatch job
    job_id = await dispatch(JobKind.plan_generation, test_user.id, mock_success_work, db_session, background_tasks)
    
    # Assert queued state
    job_db = (await db_session.execute(select(Job).where(Job.id == job_id))).scalar_one()
    assert job_db.status == JobStatus.queued
    
    # Run the background tasks manually
    for task in background_tasks.tasks:
        await task.func(*task.args, **task.kwargs)
        
    # Assert success state
    await db_session.refresh(job_db)
    assert job_db.status == JobStatus.succeeded
    assert job_db.progress == 100
    assert job_db.result is not None
    assert "plan_id" in job_db.result

@pytest.mark.asyncio
async def test_job_timeout(db_session: AsyncSession, test_user, background_tasks, monkeypatch):
    # Monkeypatch the timeout in _run_job
    import services.api.jobs.runner as runner
    monkeypatch.setattr(runner, "async_session", lambda: mock_session_maker(db_session))
    original_wait_for = asyncio.wait_for
    
    async def fast_wait_for(aw, timeout):
        return await original_wait_for(aw, timeout=0.2)
        
    monkeypatch.setattr(runner.asyncio, "wait_for", fast_wait_for)
    
    job_id = await dispatch(JobKind.plan_generation, test_user.id, mock_timeout_work, db_session, background_tasks)
    
    for task in background_tasks.tasks:
        await task.func(*task.args, **task.kwargs)
        
    job_db = (await db_session.execute(select(Job).where(Job.id == job_id))).scalar_one()
    assert job_db.status == JobStatus.failed
    assert job_db.error["code"] == "JOB_DEADLINE_EXCEEDED"

@pytest.mark.asyncio
async def test_job_app_error(db_session: AsyncSession, test_user, background_tasks, monkeypatch):
    import services.api.jobs.runner as runner
    monkeypatch.setattr(runner, "async_session", lambda: mock_session_maker(db_session))
    job_id = await dispatch(JobKind.plan_generation, test_user.id, mock_app_error_work, db_session, background_tasks)
    
    for task in background_tasks.tasks:
        await task.func(*task.args, **task.kwargs)
        
    job_db = (await db_session.execute(select(Job).where(Job.id == job_id))).scalar_one()
    assert job_db.status == JobStatus.failed
    assert job_db.error["code"] == "TEST_ERROR"

@pytest.mark.asyncio
async def test_job_unhandled_error(db_session: AsyncSession, test_user, background_tasks, monkeypatch):
    import services.api.jobs.runner as runner
    monkeypatch.setattr(runner, "async_session", lambda: mock_session_maker(db_session))
    job_id = await dispatch(JobKind.plan_generation, test_user.id, mock_unhandled_error_work, db_session, background_tasks)
    
    for task in background_tasks.tasks:
        await task.func(*task.args, **task.kwargs)
        
    job_db = (await db_session.execute(select(Job).where(Job.id == job_id))).scalar_one()
    assert job_db.status == JobStatus.failed
    assert job_db.error["code"] == "INTERNAL_ERROR"

@pytest.mark.asyncio
async def test_get_job_endpoint(client: AsyncClient, token_headers: dict, db_session: AsyncSession, test_user, background_tasks, monkeypatch):
    import services.api.jobs.runner as runner
    monkeypatch.setattr(runner, "async_session", lambda: mock_session_maker(db_session))
    # Create a job
    job_id = await dispatch(JobKind.plan_generation, test_user.id, mock_success_work, db_session, background_tasks)
    
    # Hit the endpoint
    response = await client.get(f"/api/v1/jobs/{job_id}", headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(job_id)
    assert data["status"] == "queued"
    
    # Run tasks
    for task in background_tasks.tasks:
        await task.func(*task.args, **task.kwargs)
        
    # Check again
    response = await client.get(f"/api/v1/jobs/{job_id}", headers=token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "succeeded"

@pytest.mark.asyncio
async def test_get_job_not_found(client: AsyncClient, token_headers: dict):
    response = await client.get(f"/api/v1/jobs/{uuid.uuid4()}", headers=token_headers)
    assert response.status_code == 404
