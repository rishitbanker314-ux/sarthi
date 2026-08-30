import os
from typing import Dict, Any, Optional

from services.agents.base import run
from services.agents.schemas import AdaptationDecision, PlanChange
from services.api.models.enums import AdaptationTrigger

class AdaptorAgent:
    @staticmethod
    async def generate_decision(
        trigger: str,
        profile: Dict[str, Any],
        mastery: Dict[str, Any],
        current_plan: Dict[str, Any],
        trigger_context: Dict[str, Any]
    ) -> AdaptationDecision:
        context = {
            "trigger": trigger,
            "profile": profile,
            "mastery": mastery,
            "current_plan": current_plan,
            "trigger_context": trigger_context
        }

        def fallback_factory():
            return AdaptationDecision(
                trigger=trigger, # type: ignore
                action="no_op",
                reason="We noticed some unexpected learning patterns, but the system could not determine a safe change to make at this time.",
                timeline_impact="No change to your schedule.",
                changes=[]
            )

        return await run(
            agent_name="adaptor",
            prompt_template_path="adaptor.md",
            context=context,
            output_model=AdaptationDecision,
            model_tier="pro",
            fallback_factory=fallback_factory
        )
