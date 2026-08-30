import asyncio
import uuid
import structlog
from typing import Callable, Awaitable, Any

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from services.api.db import async_session
from services.api.models.enums import JobKind, JobStatus
from services.api.models.planner import Job
from services.api.errors import AppError

logger = structlog.get_logger(__name__)

async def _run_job(job_id: uuid.UUID, work_func: Callable[[Callable[[int, str], Awaitable[None]]], Awaitable[Any]], session_maker=None):
    """
    Background task wrapper that runs a job with a 150-second timeout,
    handles reporting, and saves the final status/result/error.
    """
    if session_maker is None:
        session_maker = async_session
        
    async with session_maker() as db:
        # Load job
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            logger.error("Job not found in background task", job_id=str(job_id))
            return
            
        # Set running
        job.status = JobStatus.running
        await db.commit()
        
        # Define report callback
        async def report(progress: int, message: str) -> None:
            # We open a fresh session or use the existing one?
            # It's better to use the existing one and commit.
            # But the job object is attached to this session.
            job.progress = progress
            job.progress_message = message
            await db.commit()
            await db.refresh(job)
            
        try:
            # Run with 150s timeout
            # work_func(report) should return an awaitable.
            task = asyncio.create_task(work_func(report))
            job_result = await asyncio.wait_for(task, timeout=150.0)
            
            # Save success
            job.status = JobStatus.succeeded
            job.progress = 100
            if job_result:
                # If result is a pydantic model, dump it to dict.
                if hasattr(job_result, "model_dump"):
                    job.result = job_result.model_dump(mode='json')
                else:
                    job.result = job_result
            await db.commit()
            
        except asyncio.TimeoutError:
            # Handle timeout
            logger.error("Job deadline exceeded", job_id=str(job_id))
            job.status = JobStatus.failed
            job.error = {
                "code": "JOB_DEADLINE_EXCEEDED",
                "message": "The job took too long to complete and was terminated.",
                "retryable": True,
                "details": {}
            }
            await db.commit()
            
        except AppError as e:
            # Structured application error
            logger.exception("AppError in job", exc_info=e, job_id=str(job_id))
            job.status = JobStatus.failed
            job.error = {
                "code": e.code,
                "message": e.message,
                "retryable": e.retryable,
                "details": e.details
            }
            await db.commit()
            
        except Exception as e:
            # Unhandled exception
            logger.exception("Unhandled exception in job", exc_info=e, job_id=str(job_id))
            job.status = JobStatus.failed
            job.error = {
                "code": "INTERNAL_ERROR",
                "message": "Something went wrong on our end.",
                "retryable": True,
                "details": {"exception": str(e)}
            }
            await db.commit()

async def dispatch(
    kind: JobKind, 
    user_id: uuid.UUID, 
    work_func: Callable[[Callable[[int, str], Awaitable[None]]], Awaitable[Any]], 
    db: AsyncSession, 
    background_tasks: BackgroundTasks
) -> uuid.UUID:
    """
    Creates the jobs row with status queued, schedules the work, and returns the job id immediately.
    """
    job = Job(
        user_id=user_id,
        kind=kind,
        status=JobStatus.queued,
        progress=0
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    background_tasks.add_task(_run_job, job.id, work_func)
    
    return job.id
