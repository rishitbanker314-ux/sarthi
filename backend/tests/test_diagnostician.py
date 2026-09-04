import os
import pytest
import json
from unittest.mock import patch, AsyncMock

from services.agents.diagnostician import get_next_action
from services.agents.schemas import DiagnosticResponse, NextQuestion, ProfileDraft, AccessibilityOptions
from services.api.config import get_settings

@pytest.fixture
def mock_gemini():
    with patch("services.agents.client.get_gemini_client") as mock:
        client_instance = AsyncMock()
        mock.return_value = client_instance
        yield client_instance

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="Opt-in live test")
async def test_diagnostician_fallback_sequence():
    """
    Test the fallback sequence by simulating a broken Gemini client (e.g. ValueError).
    """
    with patch("services.agents.client.generate_content_async", side_effect=ValueError("Simulated Error")):
        # First question
        res1 = await get_next_action([])
        assert not res1.complete
        assert res1.questions is not None
        assert "What brings you to learn with us today" in res1.questions[0].question_text

        # Some intermediate question
        res4 = await get_next_action([{"agent": "...", "learner": "..."}] * 3)
        assert not res4.complete
        assert res4.questions is not None
        assert "worked examples" in res4.questions[0].question_text
        
        # Micro-problem
        res6 = await get_next_action([{"agent": "...", "learner": "..."}] * 5)
        assert not res6.complete
        assert res6.questions is not None
        assert res6.questions[0].question_type == "micro_problem"

        # Complete
        res_complete = await get_next_action([{"agent": "...", "learner": "..."}] * 8)
        assert res_complete.complete
        assert res_complete.profile_draft is not None
        assert res_complete.profile_draft.prior_knowledge == "shaky"

@pytest.mark.asyncio
async def test_diagnostician_adaptive_logic():
    """
    Test that different transcripts yield different questions (mocked for speed/reliability).
    """
    class FakeResponse:
        def __init__(self, parsed):
            self.parsed = parsed
            self.usage_metadata = None

    async def mock_generate(*args, **kwargs):
        # We look at the transcript length in context
        transcript = kwargs.get("context", {}).get("transcript", "[]")
        transcript_obj = json.loads(transcript)

        if len(transcript_obj) == 0:
            parsed = DiagnosticResponse(
                complete=False,
                questions=[NextQuestion(question_text="Are you new to programming?", question_type="single_choice", options=["yes", "no"])]
            )
            return FakeResponse(parsed)
            
        if len(transcript_obj) == 1:
            last_answer = transcript_obj[-1].get("learner", "")
            if "yes" in last_answer.lower():
                # Adapt to beginner
                parsed = DiagnosticResponse(
                    complete=False,
                    questions=[NextQuestion(question_text="Let's start simple. What is a variable?", question_type="short_text")]
                )
            else:
                # Adapt to advanced
                parsed = DiagnosticResponse(
                    complete=False,
                    questions=[NextQuestion(question_text="Micro-problem: What does `asyncio.gather()` do?", question_type="micro_problem")]
                )
            return FakeResponse(parsed)
            
        # Complete
        parsed = DiagnosticResponse(
            complete=True,
            profile_draft=ProfileDraft(
                prior_knowledge="solid", pace="fast", representation_pref="abstract_first",
                scaffolding_pref="guided_discovery", depth_pref="depth_mastery", motivation="career",
                session_minutes=60, language="en", accessibility=AccessibilityOptions()
            )
        )
        return FakeResponse(parsed)

    with patch("services.agents.base.generate_content_async", side_effect=mock_generate):
        # Path A: Beginner
        res_a = await get_next_action([
            {"agent": "Are you new to programming?", "learner": "Yes, completely new!"}
        ])
        assert res_a.questions[0].question_text == "Let's start simple. What is a variable?"
        
        # Path B: Advanced
        res_b = await get_next_action([
            {"agent": "Are you new to programming?", "learner": "No, I have 5 years of experience."}
        ])
        assert res_b.questions[0].question_text == "Micro-problem: What does `asyncio.gather()` do?"

        # Final profile completion
        res_c = await get_next_action([
            {"agent": "Are you new to programming?", "learner": "No"},
            {"agent": "Micro-problem: ...", "learner": "It runs tasks concurrently."}
        ])
        assert res_c.complete
        assert res_c.profile_draft.prior_knowledge == "solid"
