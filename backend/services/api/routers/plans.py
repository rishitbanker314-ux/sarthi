import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from services.api.db import get_session
from services.api.auth.dependencies import get_current_user, CurrentUser
from services.api.schemas.plan import PlanResponse
from services.api.models.planner import Plan, Goal, Module, Lesson

router = APIRouter(prefix="/api/v1/plans", tags=["Plans"])

@router.get("/{plan_id}", response_model=PlanResponse, status_code=status.HTTP_200_OK)
async def get_plan(
    plan_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    query = (
        select(Plan)
        .options(
            selectinload(Plan.modules).selectinload(Module.lessons)
        )
        .join(Plan.goal)
        .where(
            Plan.id == plan_id,
            Goal.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        
    return plan

from typing import Dict, Any
from fastapi import BackgroundTasks
from services.api.models.enums import JobKind
from services.api.jobs.runner import dispatch
from services.api.jobs.replan import run_replan

@router.post("/{plan_id}/replan", status_code=status.HTTP_202_ACCEPTED, response_model=Dict[str, Any])
async def replan(
    plan_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    query = (
        select(Plan)
        .join(Plan.goal)
        .where(
            Plan.id == plan_id,
            Goal.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        
    def replan_worker(report):
        return run_replan(plan_id, current_user.id, report)

    job_id = await dispatch(JobKind.replan, current_user.id, replan_worker, db, background_tasks)
    return {"job_id": str(job_id)}
