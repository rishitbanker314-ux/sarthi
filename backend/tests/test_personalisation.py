import os
import pytest
from typing import Dict, Any

from services.agents.tutor import TutorAgent
from services.api.models.enums import Pace, RepresentationPref, ScaffoldingPref, DepthPref, Motivation

@pytest.mark.asyncio
async def test_personalisation_differences():
    if not os.environ.get("GEMINI_API_KEY") or os.environ.get("RUN_LIVE_TESTS") != "1":
        pytest.skip("Skipping personalisation integration test; RUN_LIVE_TESTS!=1 or missing API key.")
    
    agent = TutorAgent()
    
    lesson_draft = {
        "title": "Introduction to Linear Regression",
        "objective": "Understand the basic concepts of linear regression and how to fit a line to data.",
        "concept_ids": ["concept-1"],
        "est_minutes": 10
    }
    
    profile_beginner: Dict[str, Any] = {
        "prior_knowledge": {"math": "basic algebra"},
        "pace": Pace.deliberate.value,
        "representation_pref": RepresentationPref.concrete_first.value,
        "scaffolding_pref": ScaffoldingPref.guided_discovery.value,
        "depth_pref": DepthPref.breadth_survey.value,
        "motivation": Motivation.curiosity.value,
        "session_minutes": 15,
        "language": "en",
        "accessibility": {}
    }
    
    profile_expert: Dict[str, Any] = {
        "prior_knowledge": {"math": "calculus, linear algebra, statistics"},
        "pace": Pace.fast.value,
        "representation_pref": RepresentationPref.abstract_first.value,
        "scaffolding_pref": ScaffoldingPref.worked_examples.value,
        "depth_pref": DepthPref.depth_mastery.value,
        "motivation": Motivation.career.value,
        "session_minutes": 30,
        "language": "en",
        "accessibility": {}
    }
    
    # Generate lessons for both profiles
    beginner_draft = await agent.generate_lesson(lesson_draft, profile_beginner, {})
    expert_draft = await agent.generate_lesson(lesson_draft, profile_expert, {})
    
    # Assert they are structurally different
    assert beginner_draft is not None
    assert expert_draft is not None
    
    # We expect some difference in blocks, perhaps more concrete examples (like text, images) for beginners
    # and more abstract/code blocks for experts, or at least different block contents/count.
    
    # Basic check: they shouldn't just be the exact same payload
    beginner_json = beginner_draft.model_dump_json()
    expert_json = expert_draft.model_dump_json()
    
    assert beginner_json != expert_json, "Expected different outputs for different learner profiles."
