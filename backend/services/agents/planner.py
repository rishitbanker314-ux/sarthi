import json
import logging
from pathlib import Path

from services.agents.base import run
from services.agents.schemas import PlanDraft, StrictPlanDraft
from services.api.schemas.goal import GoalResponse
from services.api.schemas.learner_profile import LearnerProfileResponse
from services.api.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

FIXTURE_PATH = Path(__file__).parent.parent.parent / "fixtures" / "demo" / "planner_default.json"

def _load_fallback() -> PlanDraft:
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return PlanDraft.model_validate(data)

from typing import Callable, Awaitable

async def generate_plan(goal: GoalResponse, profile: LearnerProfileResponse, mastery: list[dict], progress_callback: Callable[[str], Awaitable[None]] | None = None) -> PlanDraft:
    """
    Generates a personalized plan for a learner using Gemini.
    """
    def fallback_factory():
        return _load_fallback()
        
    context = {
        "goal": goal.model_dump_json(),
        "profile": profile.model_dump_json(),
        "mastery": [json.dumps(m) for m in mastery]
    }

    plan = await run(
        agent_name="planner",
        prompt_template_path="planner.md",
        context=context,
        output_model=PlanDraft,
        model_tier=settings.get_agent_tier("planner"),
        fallback_factory=fallback_factory,
        strict_model=StrictPlanDraft,
        validation_context={"session_minutes": profile.session_minutes},
        progress_callback=progress_callback
    )

    return plan
