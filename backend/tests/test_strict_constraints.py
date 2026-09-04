import pytest
from pydantic import ValidationError
from unittest.mock import patch, AsyncMock

from services.agents.base import run
from services.agents.usage import usage_stats
from services.agents.schemas import PlanDraft, StrictPlanDraft, ModuleDraft, LessonDraft
from services.agents.schemas import AdaptationDecision, StrictAdaptationDecision
from services.api.config import get_settings
from pathlib import Path

@pytest.fixture(autouse=True)
def setup_prompts_dir():
    prompts_dir = Path(__file__).parent.parent / "services" / "agents" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    test_template = prompts_dir / "_test_prompt.md"
    test_template.write_text("Hello {{name}}")
    yield
    if test_template.exists():
        test_template.unlink()

@pytest.fixture
def mock_gemini():
    with patch("services.agents.client.get_gemini_client") as mock:
        client_instance = AsyncMock()
        mock.return_value = client_instance
        yield client_instance

def make_plan(num_modules=3, est_minutes=15):
    modules = []
    for i in range(num_modules):
        modules.append(ModuleDraft(
            title=f"Module {i}",
            objective="obj",
            rationale="rationale",
            lessons=[
                LessonDraft(title="Lesson 1", objective="obj", concept_names=["a"], est_minutes=est_minutes),
                LessonDraft(title="Lesson 2", objective="obj", concept_names=["b"], est_minutes=est_minutes)
            ]
        ))
    return PlanDraft(title="Plan", rationale="Rationale", modules=modules)

@pytest.mark.asyncio
async def test_guard_plan_40_modules(mock_gemini):
    class OversizedResponse:
        def __init__(self):
            # 40 modules
            self.parsed = make_plan(num_modules=40)
            self.usage_metadata = type("Usage", (), {"prompt_token_count": 10, "candidates_token_count": 10, "total_token_count": 20})()
            
    mock_gemini.aio.models.generate_content.side_effect = [
        OversizedResponse(),
        OversizedResponse()
    ]
    usage_stats._stats.clear()

    def fallback():
        return make_plan(num_modules=3)

    result = await run(
        agent_name="test_40_modules",
        prompt_template_path="_test_prompt.md",
        context={"name": "Alice"},
        output_model=PlanDraft,
        model_tier=get_settings().get_agent_tier("test"),
        strict_model=StrictPlanDraft,
        validation_context={"session_minutes": 30},
        fallback_factory=fallback
    )

    assert len(result.modules) == 3
    stats = await usage_stats.get_all()
    assert stats["test_40_modules"]["retries"] == 1
    assert stats["test_40_modules"]["fallbacks"] == 1


@pytest.mark.asyncio
async def test_guard_plan_oversized_lesson(mock_gemini):
    class OversizedLessonResponse:
        def __init__(self):
            # est_minutes = 60, session_minutes = 30
            self.parsed = make_plan(num_modules=3, est_minutes=60)
            self.usage_metadata = type("Usage", (), {"prompt_token_count": 10, "candidates_token_count": 10, "total_token_count": 20})()
            
    mock_gemini.aio.models.generate_content.side_effect = [
        OversizedLessonResponse(),
        OversizedLessonResponse()
    ]
    usage_stats._stats.clear()

    def fallback():
        return make_plan(num_modules=3, est_minutes=30)

    result = await run(
        agent_name="test_oversized_lesson",
        prompt_template_path="_test_prompt.md",
        context={"name": "Alice"},
        output_model=PlanDraft,
        model_tier=get_settings().get_agent_tier("test"),
        strict_model=StrictPlanDraft,
        validation_context={"session_minutes": 30},
        fallback_factory=fallback
    )

    assert result.modules[0].lessons[0].est_minutes == 30
    stats = await usage_stats.get_all()
    assert stats["test_oversized_lesson"]["retries"] == 1
    assert stats["test_oversized_lesson"]["fallbacks"] == 1


@pytest.mark.asyncio
async def test_guard_adaptation_empty_reason(mock_gemini):
    class BadResponse:
        def __init__(self):
            self.parsed = AdaptationDecision(trigger="struggling", action="extend_timeline", reason="", timeline_impact="Will add 20 minutes", changes=[]) # type: ignore
            self.usage_metadata = type("Usage", (), {"prompt_token_count": 10, "candidates_token_count": 10, "total_token_count": 20})()

    mock_gemini.aio.models.generate_content.side_effect = [BadResponse(), BadResponse()]
    usage_stats._stats.clear()

    def fallback():
        return AdaptationDecision(trigger="struggling", action="no_op", reason="Fallback reason.", timeline_impact="Fallback impact", changes=[]) # type: ignore

    result = await run(
        agent_name="test_empty_reason",
        prompt_template_path="_test_prompt.md",
        context={"name": "Alice"},
        output_model=AdaptationDecision,
        model_tier=get_settings().get_agent_tier("test"),
        strict_model=StrictAdaptationDecision,
        fallback_factory=fallback
    )
    
    assert result.reason == "Fallback reason."
    stats = await usage_stats.get_all()
    assert stats["test_empty_reason"]["retries"] == 1
    assert stats["test_empty_reason"]["fallbacks"] == 1


@pytest.mark.asyncio
async def test_guard_adaptation_empty_timeline_impact(mock_gemini):
    class BadResponse:
        def __init__(self):
            # reason is long enough, timeline_impact is empty
            self.parsed = AdaptationDecision(trigger="struggling", action="extend_timeline", reason="X"*65, timeline_impact="", changes=[]) # type: ignore
            self.usage_metadata = type("Usage", (), {"prompt_token_count": 10, "candidates_token_count": 10, "total_token_count": 20})()

    mock_gemini.aio.models.generate_content.side_effect = [BadResponse(), BadResponse()]
    usage_stats._stats.clear()

    def fallback():
        return AdaptationDecision(trigger="struggling", action="no_op", reason="Fallback reason.", timeline_impact="Fallback impact", changes=[]) # type: ignore

    result = await run(
        agent_name="test_empty_impact",
        prompt_template_path="_test_prompt.md",
        context={"name": "Alice"},
        output_model=AdaptationDecision,
        model_tier=get_settings().get_agent_tier("test"),
        strict_model=StrictAdaptationDecision,
        fallback_factory=fallback
    )
    
    assert result.timeline_impact == "Fallback impact"
    stats = await usage_stats.get_all()
    assert stats["test_empty_impact"]["retries"] == 1
    assert stats["test_empty_impact"]["fallbacks"] == 1
