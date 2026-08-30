import pytest
from pydantic import ValidationError

from services.agents.schemas import LessonContentDraft, ContentBlock
from services.agents.tutor import TutorAgent
import uuid
import json

from services.api.models import Lesson, User, LearnerProfile, LessonContent, Goal, Plan, Module, TutorThread, TutorMessage
from services.api.models.enums import Pace, RepresentationPref, ScaffoldingPref, DepthPref, Motivation, MessageRole

def test_unknown_block_type_fails_parsing():
    # Attempt to parse a block with an invalid type
    invalid_data = {
        "blocks": [
            {
                "id": "blk_123e4567-e89b-12d3-a456-426614174000",
                "type": "invalid_type",
                "text": "Hello"
            }
        ]
    }
    
    with pytest.raises(ValidationError):
        LessonContentDraft.model_validate(invalid_data)

@pytest.mark.asyncio
async def test_tutor_agent_respects_representation_pref():
    # Need to run with DEMO_MODE = false for this test to hit the real model
    import os
    from services.api.config import get_settings
    
    # We temporarily patch DEMO_MODE for this test
    settings = get_settings()
    original_demo_mode = settings.demo_mode
    settings.demo_mode = False
    
    try:
        agent = TutorAgent()
        
        lesson_draft = {
            "title": "Introduction to Variables",
            "objective": "Understand what a variable is and how to assign a value.",
            "concept_names": ["variables", "assignment"],
            "est_minutes": 5
        }
        
        # Profile 1: concrete_first
        profile_concrete = {
            "prior_knowledge": "none",
            "pace": "standard",
            "representation_pref": "concrete_first",
            "scaffolding_pref": "guided_discovery",
            "depth_pref": "breadth_survey",
            "motivation": "curiosity",
            "session_minutes": 5,
            "language": "en",
            "accessibility": {
                "font_scale": 1.0,
                "reduced_motion": False,
                "screen_reader": False,
                "dyslexia_font": False
            }
        }
        
        # Profile 2: abstract_first
        profile_abstract = dict(profile_concrete)
        profile_abstract["representation_pref"] = "abstract_first"
        
        # Generate both
        # Note: In a real test suite, you might want to mock the LLM or mark this test as slow/integration
        # Since the instructions explicitly demand:
        # "Two profiles differing ONLY in representation_pref produce a DIFFERENT FIRST BLOCK TYPE. Assert on the type... If this test cannot be made to pass, our personalisation is decorative and I need to know now."
        # We will call the actual model.
        
        res_concrete = await agent.generate_lesson(lesson_draft, profile_concrete)
        res_abstract = await agent.generate_lesson(lesson_draft, profile_abstract)
        
        # 1. Output parses into the discriminated union - guaranteed by the typed return
        assert isinstance(res_concrete, LessonContentDraft)
        assert isinstance(res_abstract, LessonContentDraft)
        
        # 2. Exactly one ai_notice callout is present
        ai_notices_concrete = [b for b in res_concrete.blocks if b.type == "callout" and b.variant == "ai_notice"]
        assert len(ai_notices_concrete) == 1, "Must contain exactly one ai_notice callout"
        
        ai_notices_abstract = [b for b in res_abstract.blocks if b.type == "callout" and b.variant == "ai_notice"]
        assert len(ai_notices_abstract) == 1, "Must contain exactly one ai_notice callout"
        
        # 3. DIFFERENT FIRST BLOCK TYPE based on representation_pref
        first_concrete_type = res_concrete.blocks[0].type
        first_abstract_type = res_abstract.blocks[0].type
        
        # The abstract one should start with heading, text or callout (rule first).
        # The concrete one should start with example or analogy.
        # At minimum, they must be different.
        assert first_concrete_type != first_abstract_type, (
            f"Expected different starting blocks. Got concrete: {first_concrete_type}, abstract: {first_abstract_type}"
        )
        
    finally:
        settings.demo_mode = original_demo_mode

@pytest.mark.asyncio
async def test_tutor_chat_endpoints(client, db_session, test_user, token_headers):
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
    
    from unittest.mock import AsyncMock, patch
    with patch("services.api.routers.tutor.tutor_agent.chat_reply", new_callable=AsyncMock) as mock_chat:
        from services.agents.schemas import TutorChatDraft
        mock_chat.return_value = TutorChatDraft(
            message="Hello! How can I help you today?",
            blocks=[]
        )
        
        req_data = {
            "lesson_id": str(lesson.id),
            "content": "Hi there!"
        }
        
        # Test sending a message (creates a thread)
        response = await client.post(f"/api/v1/tutor/messages", json=req_data, headers=token_headers)
        assert response.status_code == 200
        
        content = response.text
        assert "event: token" in content
        assert "Hello!" in content
        assert "event: done" in content
        
        # Parse thread_id from done event
        import re
        match = re.search(r'data: (.*"thread_id":\s*"(.*?)".*)', content)
        assert match is not None
        done_data = json.loads(match.group(1))
        thread_id = done_data["thread_id"]
        
        mock_chat.assert_called_once()
        
        # Test fetching thread
        thread_res = await client.get(f"/api/v1/tutor/threads/{thread_id}", headers=token_headers)
        assert thread_res.status_code == 200
        thread_data = thread_res.json()
        
        assert thread_data["id"] == thread_id
        assert len(thread_data["messages"]) == 2
        assert thread_data["messages"][0]["role"] == "user"
        assert thread_data["messages"][0]["content"] == "Hi there!"
        assert thread_data["messages"][1]["role"] == "assistant"
        assert thread_data["messages"][1]["content"] == "Hello! How can I help you today?"
