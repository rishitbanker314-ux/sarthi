import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from uuid import UUID
import uuid

from services.agents.base import run
from services.agents.schemas import CheckpointDraft, EvaluationDraft, StrictCheckpointDraft, StrictEvaluationDraft
from services.api.config import get_settings

logger = logging.getLogger(__name__)

def get_checkpoint_fallback_data() -> CheckpointDraft:
    return CheckpointDraft.model_validate({
        "items": [
            {
                "id": str(uuid.uuid4()),
                "type": "multiple_choice",
                "question": "What is 2 + 2?",
                "options": ["3", "4", "5"],
                "concept_ids": []
            }
        ]
    })

def get_evaluation_fallback_data() -> EvaluationDraft:
    return EvaluationDraft.model_validate({
        "score": 1.0,
        "mastery_deltas": [],
        "feedback": []
    })

class AssessorAgent:
    async def generate_checkpoint(
        self,
        lesson_data: Dict[str, Any],
        profile: Dict[str, Any],
        recent_signals: List[Dict[str, Any]]
    ) -> CheckpointDraft:
        """
        Generate an interactive checkpoint for the lesson.
        """
        settings = get_settings()
        if settings.demo_mode:
            logger.info("DEMO_MODE is active, using fallback checkpoint.")
            return get_checkpoint_fallback_data()

        context = {
            "lesson_data": json.dumps(lesson_data, indent=2),
            "learner_profile": json.dumps(profile, indent=2),
            "recent_signals": json.dumps(recent_signals, indent=2)
        }

        return await run(
            agent_name="assessor_generate",
            prompt_template_path="assessor_generate.md",
            context=context,
            output_model=CheckpointDraft,
            model_tier=settings.get_agent_tier("assessor"),
            fallback_factory=get_checkpoint_fallback_data,
            strict_model=StrictCheckpointDraft
        )

    async def evaluate_checkpoint(
        self,
        checkpoint_items: List[Dict[str, Any]],
        user_responses: Dict[str, Any]
    ) -> EvaluationDraft:
        """
        Evaluate the learner's responses to the checkpoint.
        """
        settings = get_settings()
        if settings.demo_mode:
            logger.info("DEMO_MODE is active, using fallback evaluation.")
            return get_evaluation_fallback_data()

        context = {
            "checkpoint_items": json.dumps(checkpoint_items, indent=2),
            "user_responses": json.dumps(user_responses, indent=2)
        }

        return await run(
            agent_name="assessor_evaluate",
            prompt_template_path="assessor_evaluate.md",
            context=context,
            output_model=EvaluationDraft,
            model_tier=settings.get_agent_tier("assessor"),
            fallback_factory=get_evaluation_fallback_data,
            strict_model=StrictEvaluationDraft
        )
