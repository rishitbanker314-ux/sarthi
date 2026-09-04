import os
from typing import Dict, Any, Optional

from services.agents.base import run
from services.agents.schemas import AdaptationDecision, PlanChange, StrictAdaptationDecision
from services.api.models.enums import AdaptationTrigger
from services.api.config import get_settings

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
            try:
                return AdaptationDecision(
                    trigger="struggling",
                    action="no_op",
                    reason="We noticed some unexpected learning patterns, but the system could not determine a safe change to make at this time.",
                    timeline_impact="No change to your schedule.",
                    changes=[]
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Fallback construction failed: {e}")
                return AdaptationDecision.model_construct(
                    trigger="struggling",
                    action="no_op",
                    reason="We noticed some unexpected learning patterns, but the system could not determine a safe change to make at this time.",
                    timeline_impact="No change to your schedule.",
                    changes=[]
                )

        settings = get_settings()

        return await run(
            agent_name="adaptor",
            prompt_template_path="adaptor.md",
            context=context,
            output_model=AdaptationDecision,
            model_tier=settings.get_agent_tier("adaptor"),
            fallback_factory=fallback_factory,
            strict_model=StrictAdaptationDecision
        )
