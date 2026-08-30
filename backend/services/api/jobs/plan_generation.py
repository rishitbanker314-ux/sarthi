import uuid
import asyncio
from typing import Callable, Awaitable
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from services.api.db import async_session
from services.api.models.planner import Goal, Plan, Module, Lesson
from services.api.models.learner_profile import LearnerProfile
from services.api.models.concept import Concept
from services.agents.planner import generate_plan
from services.api.schemas.goal import GoalResponse
from services.api.schemas.learner_profile import LearnerProfileResponse

def get_plan_generation_worker(goal_id: uuid.UUID, user_id: uuid.UUID) -> Callable[[Callable[[int, str], Awaitable[None]]], Awaitable[None]]:
    async def worker(report: Callable[[int, str], Awaitable[None]]) -> None:
        async with async_session() as db:
            await report(10, "Reading your profile")
            
            # Load Goal
            goal_result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id))
            goal = goal_result.scalar_one_or_none()
            if not goal:
                raise Exception("Goal not found")
                
            # Load Profile
            profile_result = await db.execute(
                select(LearnerProfile)
                .where(LearnerProfile.user_id == user_id)
                .order_by(LearnerProfile.profile_version.desc())
                .limit(1)
            )
            profile = profile_result.scalar_one_or_none()
            if not profile:
                raise Exception("Active profile not found")

            # Determine next version
            plan_result = await db.execute(select(Plan).where(Plan.goal_id == goal_id).order_by(Plan.version.desc()).limit(1))
            last_plan = plan_result.scalar_one_or_none()
            next_version = last_plan.version + 1 if last_plan else 1

            # Build request schemas
            goal_response = GoalResponse.model_validate(goal, from_attributes=True)
            profile_response = LearnerProfileResponse.model_validate(profile, from_attributes=True)
            
            await report(25, "Mapping prerequisites")
            await asyncio.sleep(0.5) # Simulate time to read
            
            await report(55, "Sequencing modules")
            
            # Generate Plan using Agent
            plan_draft = await generate_plan(goal_response, profile_response, mastery=[])
            
            await report(80, "Writing lesson objectives")
            
            # Create DB Objects
            new_plan = Plan(
                goal_id=goal_id,
                version=next_version,
                title=plan_draft.title,
                rationale=plan_draft.rationale,
                profile_version=profile.profile_version,
                status="draft"
            )
            db.add(new_plan)
            
            for m_idx, module_draft in enumerate(plan_draft.modules):
                new_module = Module(
                    plan=new_plan,
                    order_index=m_idx,
                    title=module_draft.title,
                    objective=module_draft.objective,
                    rationale=module_draft.rationale,
                    est_minutes=sum(l.est_minutes for l in module_draft.lessons),
                    status="draft"
                )
                db.add(new_module)
                
                for l_idx, lesson_draft in enumerate(module_draft.lessons):
                    # Upsert Concepts
                    concept_ids = []
                    for concept_name in lesson_draft.concept_names:
                        c_result = await db.execute(select(Concept).where(Concept.name == concept_name))
                        concept = c_result.scalar_one_or_none()
                        if not concept:
                            concept = Concept(name=concept_name, description="", domain="auto")
                            db.add(concept)
                            await db.flush() # Get the concept.id
                        concept_ids.append(concept.id)
                    
                    new_lesson = Lesson(
                        module=new_module,
                        order_index=l_idx,
                        title=lesson_draft.title,
                        objective=lesson_draft.objective,
                        est_minutes=lesson_draft.est_minutes,
                        concept_ids=concept_ids,
                        status="draft"
                    )
                    db.add(new_lesson)
            
            await db.commit()
            await report(100, "Done")
            return {"plan_id": str(new_plan.id)}

    return worker
