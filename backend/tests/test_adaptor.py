import os
import pytest
from unittest.mock import patch

from services.agents.adaptor import AdaptorAgent
from services.agents.schemas import AdaptationDecision
from services.api.config import get_settings

@pytest.fixture
def demo_mode_env(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()

@pytest.fixture
def base_context():
    return {
        "trigger": "struggling",
        "profile": {},
        "mastery": {},
        "current_plan": {},
        "trigger_context": {"concept": "recursion base cases", "score": 0.4}
    }

@pytest.mark.asyncio
async def test_adaptor_generates_decision(demo_mode_env, base_context):
    decision = await AdaptorAgent.generate_decision(**base_context)
    
    assert isinstance(decision, AdaptationDecision)
    assert len(decision.reason) >= 60
    assert len(decision.timeline_impact) >= 20
    assert "recursion base cases" in decision.reason

@pytest.mark.asyncio
async def test_adaptor_generic_reason_detector(demo_mode_env, base_context):
    # The prompt mandates testing the detector. 
    bad_phrases = [
        "based on your performance",
        "tailored to you",
        "to help you learn better",
        "your learning style"
    ]
    
    # Check that demo output doesn't contain bad phrases
    decision = await AdaptorAgent.generate_decision(**base_context)
    reason_lower = decision.reason.lower()
    for phrase in bad_phrases:
        assert phrase not in reason_lower, f"Generic phrase '{phrase}' found in reason"

@pytest.mark.asyncio
async def test_adaptor_fallback_never_raises(base_context):
    # Disable demo mode for this test, force a failure in the client
    get_settings.cache_clear()
    
    with patch("services.agents.base.generate_content_async", side_effect=Exception("API Error")):
        decision = await AdaptorAgent.generate_decision(**base_context)
        assert decision.action == "no_op"
        assert decision.reason == "We noticed some unexpected learning patterns, but the system could not determine a safe change to make at this time."
        assert decision.timeline_impact == "No change to your schedule."
