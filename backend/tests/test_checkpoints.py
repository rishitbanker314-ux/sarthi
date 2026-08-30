import pytest
import uuid
import json
from httpx import AsyncClient

from services.api.models import User, LearnerProfile, Goal, Plan, Module, Lesson, Checkpoint, MasteryState
from services.api.models.enums import Pace, RepresentationPref, ScaffoldingPref, DepthPref, Motivation

@pytest.mark.asyncio
async def test_checkpoint_generation_and_evaluation(client: AsyncClient, db_session, test_user, token_headers):
    user = test_user
    
    profile = LearnerProfile(
        user_id=user.id,
        profile_version=1,
        prior_knowledge={"none": True},
        pace=Pace.standard,
        representation_pref=RepresentationPref.concrete_first,
        scaffolding_pref=ScaffoldingPref.guided_discovery,
        depth_pref=DepthPref.breadth_survey,
        motivation=Motivation.curiosity,
        session_minutes=5,
        language="en",
        accessibility={
            "font_scale": 1.0,
            "reduced_motion": False,
            "screen_reader": False,
            "dyslexia_font": False
        }
    )
    db_session.add(profile)
    
    goal = Goal(id=uuid.uuid4(), user_id=user.id, raw_input="t", normalized_topic="t", target_level="t", status="active")
    db_session.add(goal)
    plan = Plan(id=uuid.uuid4(), goal_id=goal.id, version=1, title="t", rationale="t", profile_version=1, status="active")
    db_session.add(plan)
    module = Module(id=uuid.uuid4(), plan_id=plan.id, order_index=0, title="t", objective="t", rationale="t", est_minutes=5, status="active")
    db_session.add(module)
    
    from services.api.models import Concept
    
    concept_id = uuid.uuid4()
    concept = Concept(id=concept_id, name="Test Concept", description="Test", domain="Test Domain")
    db_session.add(concept)
    lesson = Lesson(id=uuid.uuid4(), module_id=module.id, order_index=0, title="T", objective="T", concept_ids=[concept_id], est_minutes=5, status="planned")
    db_session.add(lesson)
    await db_session.commit()

    from unittest.mock import AsyncMock, patch
    with patch("services.api.routers.checkpoints.AssessorAgent.generate_checkpoint", new_callable=AsyncMock) as mock_gen, \
         patch("services.api.routers.checkpoints.AssessorAgent.evaluate_checkpoint", new_callable=AsyncMock) as mock_eval:
        
        from services.agents.schemas import CheckpointDraft, CheckpointItemDraft, EvaluationDraft, MasteryDeltaDraft, ItemFeedbackDraft
        
        item_id = str(uuid.uuid4())
        mock_gen.return_value = CheckpointDraft(
            items=[
                CheckpointItemDraft(
                    id=item_id,
                    type="multiple_choice",
                    question="What is 2+2?",
                    options=["3", "4", "5"],
                    concept_ids=[concept_id]
                )
            ]
        )
        
        # Test generate
        resp = await client.post(f"/api/v1/lessons/{lesson.id}/checkpoint", headers=token_headers)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "id" in data
        checkpoint_id = data["id"]
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == item_id
        
        mock_eval.return_value = EvaluationDraft(
            score=1.0,
            mastery_deltas=[
                MasteryDeltaDraft(concept_id=concept_id, delta=0.2)
            ],
            feedback=[
                ItemFeedbackDraft(item_id=item_id, correct=True, explanation="Good")
            ]
        )
        
        # Test evaluate
        req_data = {
            "responses": {
                item_id: "4"
            }
        }
        
        eval_resp = await client.post(f"/api/v1/checkpoints/{checkpoint_id}/submit", json=req_data, headers=token_headers)
        assert eval_resp.status_code == 200
        eval_data = eval_resp.json()
        
        assert eval_data["score"] == 1.0
        assert len(eval_data["mastery_deltas"]) == 1
        assert eval_data["mastery_deltas"][0]["concept_id"] == str(concept_id)
        assert eval_data["mastery_deltas"][0]["delta"] == 0.2
        
        # Verify DB MasteryState
        from sqlalchemy import select
        mastery_res = await db_session.execute(select(MasteryState).where(MasteryState.user_id == user.id, MasteryState.concept_id == concept_id))
        mastery = mastery_res.scalar_one_or_none()
        
        assert mastery is not None
        assert mastery.score == 0.7  # 0.5 + 0.2
