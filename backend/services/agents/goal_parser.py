import logging
from typing import Optional

from services.agents.base import run
from services.agents.schemas import GoalParse

logger = logging.getLogger(__name__)

async def parse_goal(raw_input: str) -> GoalParse:
    """
    Parses a user's raw input into a structured GoalParse object using the Goal Parser Agent.
    """
    def fallback() -> GoalParse:
        # Fallback if the model fails
        topic = raw_input[:50]
        return GoalParse(
            normalized_topic=topic,
            target_level="beginner",
            deadline=None,
            motivation_hint=None,
            is_educational=True,
            clarification_needed=None
        )

    from services.api.config import get_settings
    settings = get_settings()

    return await run(
        agent_name="goal_parser",
        prompt_template_path="goal_parser.md",
        context={"raw_input": raw_input},
        output_model=GoalParse,
        model_tier=settings.get_agent_tier("goal_parser"),
        fallback_factory=fallback
    )
