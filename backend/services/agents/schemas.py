from typing import Literal, Optional, List
from pydantic import BaseModel, Field

# -------------------------
# Diagnostician Schemas
# -------------------------

class AccessibilityOptions(BaseModel):
    font_scale: float = Field(default=1.0, ge=1.0, le=2.0, description="Multiplies all rem type sizes")
    reduced_motion: bool = Field(default=False, description="No transitions, autoplay or parallax")
    screen_reader: bool = Field(default=False, description="Verbose aria-live announcements")
    dyslexia_font: bool = Field(default=False, description="Switches lesson body to a dyslexia-friendly face")

class ProfileDraft(BaseModel):
    prior_knowledge: Literal["none", "shaky", "solid"] = Field(description="The single strongest predictor of what to teach next.")
    pace: Literal["deliberate", "standard", "fast"] = Field(description="Controls lesson granularity and step size.")
    representation_pref: Literal["concrete_first", "abstract_first"] = Field(description="Example-then-rule vs rule-then-example.")
    scaffolding_pref: Literal["worked_examples", "guided_discovery"] = Field(description="How much to show before asking.")
    depth_pref: Literal["breadth_survey", "depth_mastery"] = Field(description="Shapes plan width.")
    motivation: Literal["exam", "career", "curiosity", "project"] = Field(description="Changes framing and what gets cut.")
    session_minutes: int = Field(description="Hard budget per lesson.")
    language: str = Field(description="BCP-47 tag for explanation language.")
    accessibility: AccessibilityOptions = Field(description="Accessibility settings")

class NextQuestion(BaseModel):
    question_text: str = Field(description="The actual question to ask the learner.")
    question_type: Literal["single_choice", "multi_choice", "scale", "short_text", "micro_problem"] = Field(description="The format of the question.")
    options: Optional[List[str]] = Field(default=None, description="Provide options if the type is single_choice or multi_choice. Otherwise null.")

class DiagnosticResponse(BaseModel):
    complete: bool = Field(description="Set to true ONLY if you have enough information to derive all ProfileDraft fields.")
    question: Optional[NextQuestion] = Field(default=None, description="The next question to ask. Required if complete is false.")
    profile_draft: Optional[ProfileDraft] = Field(default=None, description="The derived profile. Required if complete is true.")
