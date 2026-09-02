import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from uuid import UUID

from services.agents.base import run
from services.agents.schemas import LessonContentDraft, ReexplainDraft, TutorChatDraft
from services.api.config import get_settings

logger = logging.getLogger(__name__)

def get_fallback_data() -> LessonContentDraft:
    settings = get_settings()
    # In a real app we'd get BASE_DIR properly, for now assume relative or set it.
    fallback_path = Path(__file__).parent.parent.parent / "fixtures" / "demo" / "tutor_default.json"
    if fallback_path.exists():
        with open(fallback_path, "r") as f:
            data = json.load(f)
            return LessonContentDraft.model_validate(data)
    else:
        return LessonContentDraft.model_validate({
            "blocks": [
                {
                    "id": "blk_00000000-0000-0000-0000-000000000000",
                    "type": "heading",
                    "text": "Fallback Lesson",
                    "level": 1
                },
                {
                    "id": "blk_00000000-0000-0000-0000-000000000001",
                    "type": "text",
                    "text": "The lesson content could not be generated."
                },
                {
                    "id": "blk_00000000-0000-0000-0000-000000000002",
                    "type": "callout",
                    "variant": "ai_notice",
                    "title": "AI Notice",
                    "text": "This is an AI generated fallback."
                }
            ]
        })

def get_reexplain_fallback_data() -> ReexplainDraft:
    return ReexplainDraft.model_validate({
        "reexplain_strategy": "fallback strategy",
        "blocks": [
            {
                "id": "blk_00000000-0000-0000-0000-000000000003",
                "type": "text",
                "text": "Fallback re-explanation content."
            }
        ]
    })

def get_chat_fallback_data() -> TutorChatDraft:
    return TutorChatDraft.model_validate({
        "message": "This is a fallback chat reply.",
        "blocks": []
    })

class TutorAgent:
    async def generate_lesson(
        self,
        lesson_draft: Dict[str, Any],
        profile: Dict[str, Any],
        mastery_state: Optional[Dict[str, Any]] = None,
        job_id: Optional[UUID] = None
    ) -> LessonContentDraft:
        """
        Generate a lesson content draft.
        """
        settings = get_settings()
        if settings.demo_mode:
            logger.info("DEMO_MODE is active, using fallback tutor content.")
            return get_fallback_data()

        # Assemble the input
        prompt_data = {
            "lesson_plan": lesson_draft,
            "learner_profile": profile,
            "mastery_state": mastery_state or {}
        }
        
        # In base.py, context gets substituted like {{key}}. So we format the data as JSON strings.
        context = {
            "lesson_plan": json.dumps(lesson_draft, indent=2, default=str),
            "learner_profile": json.dumps(profile, indent=2, default=str),
            "mastery_state": json.dumps(mastery_state or {}, indent=2, default=str)
        }

        return await run(
            agent_name="tutor",
            prompt_template_path="tutor.md",
            context=context,
            output_model=LessonContentDraft,
            model_tier="flash",
            fallback_factory=get_fallback_data
        )

    async def reexplain_block(
        self,
        original_block: Dict[str, Any],
        profile: Dict[str, Any],
        reason: Optional[str] = None
    ) -> ReexplainDraft:
        """
        Generate a re-explanation for a specific block.
        """
        settings = get_settings()
        if settings.demo_mode:
            logger.info("DEMO_MODE is active, using fallback reexplain content.")
            return get_reexplain_fallback_data()
            
        context = {
            "original_block": json.dumps(original_block, indent=2, default=str),
            "learner_profile": json.dumps(profile, indent=2, default=str),
            "reason": reason or "No reason provided"
        }
        
        return await run(
            agent_name="tutor_reexplain",
            prompt_template_path="reexplain.md",
            context=context,
            output_model=ReexplainDraft,
            model_tier="flash",
            fallback_factory=get_reexplain_fallback_data
        )

    async def chat_reply(
        self,
        message: str,
        history: List[Dict[str, Any]],
        profile: Dict[str, Any],
        context_block: Optional[Dict[str, Any]] = None
    ) -> TutorChatDraft:
        """
        Generate a conversational reply from the tutor.
        """
        settings = get_settings()
        if settings.demo_mode:
            logger.info("DEMO_MODE is active, using fallback chat content.")
            return get_chat_fallback_data()
            
        context = {
            "message": message,
            "history": json.dumps(history, indent=2, default=str),
            "learner_profile": json.dumps(profile, indent=2, default=str),
            "context_block": json.dumps(context_block, indent=2, default=str) if context_block else "None"
        }
        
        return await run(
            agent_name="tutor_chat",
            prompt_template_path="tutor_chat.md",
            context=context,
            output_model=TutorChatDraft,
            model_tier="flash",
            fallback_factory=get_chat_fallback_data
        )
