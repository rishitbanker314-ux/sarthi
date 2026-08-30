import json
import logging
from pathlib import Path

from services.agents.base import run
from services.agents.schemas import PlanDraft
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

async def generate_plan(goal: GoalResponse, profile: LearnerProfileResponse, mastery: list[dict]) -> PlanDraft:
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
        model_tier="pro",
        fallback_factory=fallback_factory
    )

    # Extra programmatic check: Ensure est_minutes <= session_minutes
    for module in plan.modules:
        for lesson in module.lessons:
            if lesson.est_minutes > profile.session_minutes:
                logger.warning(f"Lesson '{lesson.title}' exceeds session minutes ({lesson.est_minutes} > {profile.session_minutes}). Capping.")
                lesson.est_minutes = profile.session_minutes

    return plan
