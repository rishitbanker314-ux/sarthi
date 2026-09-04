import pytest
from pydantic import ValidationError
from services.agents.schemas import StrictPlanDraft, ModuleDraft, LessonDraft, StrictAdaptationDecision

def test_guard_plan_40_modules():
    modules = []
    for i in range(40):
        modules.append(ModuleDraft(
            title=f"Module {i}",
            objective="obj",
            rationale="rationale",
            lessons=[LessonDraft(title="L", objective="obj", concept_names=["a"], est_minutes=15)]
        ))
    
    with pytest.raises(ValidationError) as exc_info:
        StrictPlanDraft(title="Plan", rationale="Rationale", modules=modules)
    
    assert "modules" in str(exc_info.value)

def test_guard_lesson_over_block_limit():
    modules = [
        ModuleDraft(
            title="Module 1",
            objective="obj",
            rationale="rationale",
            lessons=[LessonDraft(title="L", objective="obj", concept_names=["a"], est_minutes=120)]
        )
    ]
    
    with pytest.raises(ValidationError) as exc_info:
        # Context is required for session_minutes
        StrictPlanDraft.model_validate({"title": "Plan", "rationale": "Rationale", "modules": modules}, context={"session_minutes": 30})
    
    assert "est_minutes" in str(exc_info.value) or "Value error" in str(exc_info.value)

def test_guard_adaptation_empty_reason():
    with pytest.raises(ValidationError) as exc_info:
        StrictAdaptationDecision(trigger="struggling", action="extend_timeline", reason="", timeline_impact="Will add 20 minutes", changes=[]) # type: ignore
    
    assert "reason" in str(exc_info.value) or "String should have at least" in str(exc_info.value)

def test_guard_adaptation_empty_timeline_impact():
    with pytest.raises(ValidationError) as exc_info:
        StrictAdaptationDecision(trigger="struggling", action="extend_timeline", reason="This is a valid long reason for adaptation", timeline_impact="", changes=[]) # type: ignore
    
    assert "timeline_impact" in str(exc_info.value) or "String should have at least" in str(exc_info.value)
