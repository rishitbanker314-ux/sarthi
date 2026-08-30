import uuid
from typing import Callable, Awaitable, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from services.api.db import async_session
from services.api.models.planner import Plan, Module, Lesson
from services.api.models.lesson_execution import LessonContent
from services.api.models.adaptation import AdaptationEvent
from services.api.models.learner_profile import LearnerProfile
from services.api.models.enums import AdaptationAction
from services.api.adaptation.triggers import evaluate
from services.agents.adaptor import AdaptorAgent
from services.api.schemas.job import ReplanResult

async def run_replan(plan_id: uuid.UUID, user_id: uuid.UUID, report: Callable[[int, str], Awaitable[None]], lesson_id: Optional[uuid.UUID] = None) -> ReplanResult | None:
    async with async_session() as db:
        await report(10, "Loading current plan")
        
        # 1. Load Plan with Modules and Lessons
        query = (
            select(Plan)
            .options(selectinload(Plan.modules).selectinload(Module.lessons))
            .where(Plan.id == plan_id)
        )
        result = await db.execute(query)
        old_plan = result.scalar_one_or_none()
        
        if not old_plan:
            raise Exception("Plan not found")
            
        await report(20, "Evaluating triggers")
        
        # 2. Evaluate triggers
        # Just passing lesson_id to evaluate user-wide triggers (like struggling, racing, stalled)
        trigger_result = await evaluate(user_id, lesson_id, db)
        
        if not trigger_result:
            await report(100, "No adaptation needed")
            return ReplanResult(plan_id=old_plan.id, adaptation_event_id=uuid.uuid4()) # Should not happen usually, but for type safety
            
        await report(40, "Consulting Adaptor AI")
        
        # 3. Call Adaptor
        # Need profile and mastery
        profile_result = await db.execute(
            select(LearnerProfile)
            .where(LearnerProfile.user_id == user_id)
            .order_by(LearnerProfile.profile_version.desc())
        )
        profile = profile_result.scalars().first()
        profile_dict = {}
        if profile:
            profile_dict = {
                "pace": profile.pace.value,
                "representation_pref": profile.representation_pref.value,
                "scaffolding_pref": profile.scaffolding_pref.value,
                "depth_pref": profile.depth_pref.value,
                "motivation": profile.motivation.value,
            }
        
        # We can just serialize old_plan for the agent context
        current_plan_dict = {
            "title": old_plan.title,
            "modules": [
                {
                    "id": str(m.id),
                    "title": m.title,
                    "lessons": [
                        {"id": str(l.id), "title": l.title} for l in m.lessons
                    ]
                }
                for m in old_plan.modules
            ]
        }
        
        decision = await AdaptorAgent.generate_decision(
            trigger=trigger_result.trigger.value,
            profile=profile_dict,
            mastery={}, # Stubbed mastery for now
            current_plan=current_plan_dict,
            trigger_context={}
        )
        
        await report(60, "Generating new plan version")
        
        # 4. Clone Plan
        from sqlalchemy import func
        stmt = select(func.max(Plan.version)).where(Plan.goal_id == old_plan.goal_id)
        max_version = (await db.execute(stmt)).scalar_one()
        
        new_plan = Plan(
            goal_id=old_plan.goal_id,
            version=(max_version or old_plan.version) + 1,
            title=old_plan.title,
            rationale=old_plan.rationale,
            profile_version=old_plan.profile_version,
            status="draft" # Starts as draft until accepted
        )
        db.add(new_plan)
        await db.flush()
        
        # Deep copy modules and lessons
        lesson_mapping = {} # old_id -> new_id
        for old_mod in old_plan.modules:
            new_mod = Module(
                plan_id=new_plan.id,
                order_index=old_mod.order_index,
                title=old_mod.title,
                objective=old_mod.objective,
                rationale=old_mod.rationale,
                est_minutes=old_mod.est_minutes,
                status=old_mod.status
            )
            db.add(new_mod)
            await db.flush()
            
            for old_less in old_mod.lessons:
                new_less = Lesson(
                    module_id=new_mod.id,
                    order_index=old_less.order_index,
                    title=old_less.title,
                    objective=old_less.objective,
                    concept_ids=list(old_less.concept_ids),
                    est_minutes=old_less.est_minutes,
                    status=old_less.status
                )
                db.add(new_less)
                await db.flush()
                lesson_mapping[old_less.id] = new_less.id
                
                # Copy LessonContent if exists
                content_query = select(LessonContent).where(LessonContent.lesson_id == old_less.id)
                content_result = await db.execute(content_query)
                old_content = content_result.scalar_one_or_none()
                
                if old_content:
                    new_content = LessonContent(
                        lesson_id=new_less.id,
                        profile_version=old_content.profile_version,
                        blocks=old_content.blocks,
                        token_cost=old_content.token_cost
                    )
                    db.add(new_content)
        
        # Apply PlanChanges here in a real implementation
        # (For this stubbed flow, we just copy everything)
        
        await report(80, "Saving adaptation event")
        
        # 5. Save AdaptationEvent
        event = AdaptationEvent(
            user_id=user_id,
            plan_id=new_plan.id,
            trigger=trigger_result.trigger,
            action=AdaptationAction(decision.action),
            reason=decision.reason,
            timeline_impact=decision.timeline_impact,
            before=current_plan_dict,
            after=current_plan_dict, # Real implementation would serialize new_plan
            accepted=None
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        
        await report(100, "Done")
        
        return ReplanResult(plan_id=new_plan.id, adaptation_event_id=event.id)
