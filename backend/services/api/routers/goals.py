import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from services.api.db import get_session
from services.api.auth.dependencies import get_current_user, CurrentUser
from services.api.schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from services.api.schemas.pagination import PaginatedResponse, PaginationParams, SortParams
from services.api.models.planner import Goal, Plan
from services.agents.goal_parser import parse_goal
from sqlalchemy import func
from services.api.rate_limiter import limiter

router = APIRouter(prefix="/api/v1/goals", tags=["Goals"])

@router.post("", response_model=GoalResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def create_goal(
    goal_in: GoalCreate,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    # Call the GoalParserAgent
    parsed_goal = await parse_goal(goal_in.raw_input)
    
    # Save to database
    db_goal = Goal(
        user_id=current_user.id,
        raw_input=goal_in.raw_input,
        normalized_topic=parsed_goal.normalized_topic,
        target_level=parsed_goal.target_level,
        deadline=parsed_goal.deadline,
        motivation_hint=parsed_goal.motivation_hint,
        is_educational=parsed_goal.is_educational,
        clarification_needed=parsed_goal.clarification_needed,
        status="captured"
    )
    
    db.add(db_goal)
    await db.commit()
    await db.refresh(db_goal)
    
    return db_goal

@router.get("", response_model=PaginatedResponse[GoalResponse], status_code=status.HTTP_200_OK)
async def list_goals(
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    query = select(Goal).where(Goal.user_id == current_user.id)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Apply sorting
    if sort.sort_by and hasattr(Goal, sort.sort_by):
        col = getattr(Goal, sort.sort_by)
        if sort.sort_desc:
            query = query.order_by(col.desc())
        else:
            query = query.order_by(col.asc())
    else:
        query = query.order_by(Goal.created_at.desc())
        
    # Apply pagination
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    result = await db.execute(query)
    data = result.scalars().all()
    
    return PaginatedResponse(
        data=data,
        total=total,
        page=pagination.page,
        size=pagination.size,
        has_more=total > pagination.page * pagination.size
    )

@router.patch("/{goal_id}", response_model=GoalResponse, status_code=status.HTTP_200_OK)
async def update_goal(
    goal_id: uuid.UUID,
    goal_update: GoalUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    # Check if goal exists and belongs to user
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id))
    db_goal = result.scalar_one_or_none()
    
    if not db_goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
        
    # Check if a plan already exists for this goal
    plan_result = await db.execute(select(Plan).where(Plan.goal_id == goal_id))
    if plan_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="GOAL_ALREADY_PLANNED: Cannot modify a goal that already has an associated plan."
        )
        
    # Update fields
    if goal_update.normalized_topic is not None:
        db_goal.normalized_topic = goal_update.normalized_topic
    if goal_update.target_level is not None:
        db_goal.target_level = goal_update.target_level
    if goal_update.deadline is not None:
        db_goal.deadline = goal_update.deadline
        
    await db.commit()
    await db.refresh(db_goal)
    
    return db_goal

from fastapi import BackgroundTasks
from services.api.models.enums import JobKind, JobStatus
from services.api.jobs.runner import dispatch
from services.api.jobs.plan_generation import get_plan_generation_worker

@router.post("/{goal_id}/plan", status_code=status.HTTP_202_ACCEPTED)
async def generate_plan_endpoint(
    goal_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    # Verify goal exists
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id))
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
        
    # Verify no active plan generation job exists for this user
    from services.api.models.planner import Job
    active_jobs = await db.execute(
        select(Job).where(
            Job.user_id == current_user.id,
            Job.kind == JobKind.plan_generation,
            Job.status.in_([JobStatus.queued, JobStatus.running])
        )
    )
    if active_jobs.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="PLAN_ALREADY_GENERATING"
        )
        
    # Dispatch Job
    worker = get_plan_generation_worker(goal_id, current_user.id)
    job_id = await dispatch(JobKind.plan_generation, current_user.id, worker, db, background_tasks)
    
    return {"job_id": job_id}
