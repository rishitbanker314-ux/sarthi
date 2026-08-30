import pytest
from httpx import AsyncClient, ASGITransport
import uuid
import json

from services.api.models import Lesson, User, LearnerProfile, LessonContent, Goal, Plan, Module
from services.api.models.enums import Pace, RepresentationPref, ScaffoldingPref, DepthPref, Motivation

@pytest.mark.asyncio
async def test_lesson_content_streaming_cache(client, db_session, test_user, token_headers):
    # Setup Data
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
    
    goal = Goal(
        id=uuid.uuid4(),
        user_id=user.id,
        raw_input="test",
        normalized_topic="test",
        target_level="test",
        status="active"
    )
    db_session.add(goal)
    
    plan = Plan(
        id=uuid.uuid4(),
        goal_id=goal.id,
        version=1,
        title="test",
        rationale="test",
        profile_version=1,
        status="active"
    )
    db_session.add(plan)
    
    module = Module(
        id=uuid.uuid4(),
        plan_id=plan.id,
        order_index=0,
        title="test",
        objective="test",
        rationale="test",
        est_minutes=5,
        status="active"
    )
    db_session.add(module)
    
    lesson = Lesson(
        id=uuid.uuid4(),
        module_id=module.id,
        order_index=0,
        title="Test Lesson",
        objective="Test Objective",
        concept_ids=[],
        est_minutes=5,
        status="planned"
    )
    db_session.add(lesson)
    await db_session.commit()
    
    # We'll use a mocked db for checking the calls or we can patch TutorAgent
    from unittest.mock import AsyncMock, patch
    
    with patch("services.api.routers.lessons.tutor_agent.generate_lesson", new_callable=AsyncMock) as mock_generate:
        # Mock the return value of TutorAgent to simulate a generated lesson
        from services.agents.schemas import LessonContentDraft
        mock_generate.return_value = LessonContentDraft(
            blocks=[
                {
                    "id": "blk_123e4567-e89b-12d3-a456-426614174000",
                    "type": "heading",
                    "text": "Generated Content",
                    "level": 1
                }
            ]
        )
        
        # Request 1: Cache Miss
        response = await client.get(f"/api/v1/lessons/{lesson.id}/content", headers=token_headers)
        assert response.status_code == 200
        
        content = response.text
        assert "event: block" in content
        assert "Generated Content" in content
        
        mock_generate.assert_called_once()
        mock_generate.reset_mock()
        
        # Request 2: Cache Hit
        response2 = await client.get(f"/api/v1/lessons/{lesson.id}/content", headers=token_headers)
        assert response2.status_code == 200
        
        content2 = response2.text
        assert "event: block" in content2
        assert "Generated Content" in content2
        
        # Ensure generate_lesson was NOT called again
        mock_generate.assert_not_called()

@pytest.mark.asyncio
async def test_reexplain_endpoint(client, db_session, test_user, token_headers):
    # Setup Data
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
    
    lesson = Lesson(id=uuid.uuid4(), module_id=module.id, order_index=0, title="T", objective="T", concept_ids=[], est_minutes=5, status="planned")
    db_session.add(lesson)
    await db_session.commit()
    
    # Insert mock lesson content
    block_id = uuid.uuid4()
    cached_content = LessonContent(
        lesson_id=lesson.id,
        profile_version=1,
        blocks={"blocks": [
            {
                "id": str(block_id),
                "type": "text",
                "text": "Original confusing text."
            }
        ]},
        token_cost=100
    )
    db_session.add(cached_content)
    await db_session.commit()
    
    from unittest.mock import AsyncMock, patch
    with patch("services.api.routers.lessons.tutor_agent.reexplain_block", new_callable=AsyncMock) as mock_reexplain:
        from services.agents.schemas import ReexplainDraft
        mock_reexplain.return_value = ReexplainDraft(
            reexplain_strategy="switched to analogy",
            blocks=[
                {
                    "id": "blk_123e4567-e89b-12d3-a456-426614174001",
                    "type": "text",
                    "text": "Here is an analogy instead."
                }
            ]
        )
        
        req_data = {
            "block_id": str(block_id),
            "reason": "I don't understand."
        }
        
        response = await client.post(f"/api/v1/lessons/{lesson.id}/reexplain", json=req_data, headers=token_headers)
        assert response.status_code == 200
        
        content = response.text
        assert "event: block" in content
        assert "Here is an analogy instead." in content
        assert "event: done" in content
        assert "switched to analogy" in content
        
        mock_reexplain.assert_called_once()
        
    # Check that a Signal was created
    from services.api.models import Signal
    from sqlalchemy.future import select
    result = await db_session.execute(select(Signal).where(Signal.lesson_id == lesson.id))
    signals = result.scalars().all()
    assert len(signals) == 1
    assert signals[0].type.name == "confusion_flag"
    assert signals[0].block_id == block_id
    assert signals[0].value == {"reason": "I don't understand."}

