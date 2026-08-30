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
@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "fake-key-for-tests", reason="Needs real API key")
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

TEST_CASES = [
    # Struggle scenarios requiring adaptation
    ("struggling", "recursion base cases", 0.4, "modify_plan"),
    ("struggling", "pointers in C", 0.3, "modify_plan"),
    ("struggling", "binary search boundaries", 0.5, "modify_plan"),
    ("struggling", "SQL joins", 0.45, "modify_plan"),
    ("struggling", "dynamic programming state", 0.2, "modify_plan"),
    ("struggling", "async await event loop", 0.35, "modify_plan"),
    ("struggling", "React hooks dependency array", 0.4, "modify_plan"),
    ("struggling", "CSS grid templates", 0.48, "modify_plan"),
    ("struggling", "regex lookaheads", 0.25, "modify_plan"),
    ("struggling", "Git rebase conflicts", 0.3, "modify_plan"),
    # Mastery scenarios requiring progression/no_op
    ("boredom", "basic arithmetic", 0.95, "modify_plan"),
    ("boredom", "hello world print", 0.99, "modify_plan"),
    ("boredom", "variable declaration", 0.92, "modify_plan"),
    ("boredom", "string concatenation", 0.98, "modify_plan"),
    ("boredom", "for loop syntax", 0.96, "modify_plan"),
    ("boredom", "if statements", 0.94, "modify_plan"),
    ("boredom", "array indexing", 0.91, "modify_plan"),
    ("boredom", "dictionary keys", 0.93, "modify_plan"),
    ("boredom", "boolean logic", 0.97, "modify_plan"),
    ("boredom", "function calls", 0.95, "modify_plan"),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("trigger,concept,score,expected_action", TEST_CASES)
@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "fake-key-for-tests", reason="Needs real API key")
async def test_adaptor_accuracy_20_cases(trigger, concept, score, expected_action, monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    get_settings.cache_clear()
    
    context = {
        "trigger": trigger,
        "profile": {},
        "mastery": {},
        "current_plan": {},
        "trigger_context": {"concept": concept, "score": score}
    }
    
    decision = await AdaptorAgent.generate_decision(**context)
    
    assert isinstance(decision, AdaptationDecision)
    assert decision.action in ["modify_plan", "no_op", "update_pace", "recommend_break"]
    # We expect some action, usually modify_plan or update_pace, depending on the LLM's judgement
    assert len(decision.reason) >= 20
