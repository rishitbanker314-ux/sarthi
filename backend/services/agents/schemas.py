from typing import Literal, Optional, List
from datetime import date
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

# -------------------------
# Goal Parser Schemas
# -------------------------

class GoalParse(BaseModel):
    normalized_topic: str = Field(description="The normalized topic extracted from the raw input.")
    target_level: Literal["beginner", "intermediate", "advanced"] = Field(description="The target level of the goal.")
    deadline: Optional[date] = Field(default=None, description="The deadline for the goal, if any.")
    motivation_hint: Optional[Literal["exam", "career", "curiosity", "project"]] = Field(default=None, description="The motivation behind the goal, if any.")
    is_educational: bool = Field(description="Whether the goal is educational or not.")
    clarification_needed: Optional[str] = Field(default=None, description="A friendly clarification message if the goal is not educational or needs more details.")

# -------------------------
# Planner Schemas
# -------------------------

class LessonDraft(BaseModel):
    title: str = Field(description="The title of the lesson.")
    objective: str = Field(description="A clear objective for what the learner will achieve in this lesson.")
    concept_names: List[str] = Field(description="A list of specific concepts covered in this lesson.")
    est_minutes: int = Field(ge=10, description="Estimated time in minutes to complete this lesson. Must be at least 10 minutes.")

class ModuleDraft(BaseModel):
    title: str = Field(description="The title of the module.")
    objective: str = Field(description="The overarching objective for this module.")
    rationale: str = Field(description="Why this module is sequenced here and how it helps the learner.")
    lessons: List[LessonDraft] = Field(min_length=2, max_length=6, description="The lessons in this module. Must be between 2 and 6 lessons.")

class PlanDraft(BaseModel):
    title: str = Field(description="The title of the overall learning plan.")
    rationale: str = Field(
        description="A detailed rationale for this plan. You MUST explicitly reference at least two specific dimensions from the learner's profile (e.g., 'Because you have 25 minutes a day', 'Since you prefer concrete examples first'). If the learner has prior mastery, you MUST explicitly mention which concepts were skipped or compressed."
    )
    modules: List[ModuleDraft] = Field(min_length=3, max_length=8, description="The modules in this plan. Must be between 3 and 8 modules.")

# -------------------------
# Tutor Schemas
# -------------------------

from typing import Union, Annotated
from uuid import UUID

class ContentBlockBase(BaseModel):
    id: str = Field(pattern=r"^blk_[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$")
    concept_id: Optional[UUID] = None

class HeadingBlock(ContentBlockBase):
    type: Literal["heading"]
    text: str
    level: int = Field(ge=1, le=3)

class TextBlock(ContentBlockBase):
    type: Literal["text"]
    text: str

class ListBlock(ContentBlockBase):
    type: Literal["list"]
    ordered: bool
    items: List[str]

class CodeBlock(ContentBlockBase):
    type: Literal["code"]
    language: str
    code: str
    caption: Optional[str] = None

class MathBlock(ContentBlockBase):
    type: Literal["math"]
    latex: str
    display: bool

class CalloutBlock(ContentBlockBase):
    type: Literal["callout"]
    variant: Literal["info", "tip", "warning", "misconception", "ai_notice"]
    title: str
    text: str

class ExampleBlock(ContentBlockBase):
    type: Literal["example"]
    title: str
    setup: str
    steps: List[str]
    result: str

class AnalogyBlock(ContentBlockBase):
    type: Literal["analogy"]
    text: str
    maps_to: str

class StepBlock(ContentBlockBase):
    type: Literal["step"]
    index: int
    text: str
    reveal: bool

class QuizInlineBlock(ContentBlockBase):
    type: Literal["quiz_inline"]
    question: str
    options: List[str]
    answer_index: int
    explanation: str

class ImagePromptBlock(ContentBlockBase):
    type: Literal["image_prompt"]
    alt: str
    description: str

class DividerBlock(ContentBlockBase):
    type: Literal["divider"]

ContentBlock = Union[
    HeadingBlock,
    TextBlock,
    ListBlock,
    CodeBlock,
    MathBlock,
    CalloutBlock,
    ExampleBlock,
    AnalogyBlock,
    StepBlock,
    QuizInlineBlock,
    ImagePromptBlock,
    DividerBlock
]

class LessonContentDraft(BaseModel):
    blocks: List[ContentBlock]

class ReexplainDraft(BaseModel):
    reexplain_strategy: str = Field(description="The strategy chosen to explain this block differently (e.g. 'switched to concrete analogy', 'provided general rule').")
    blocks: List[ContentBlock]

class TutorChatDraft(BaseModel):
    message: str = Field(description="The conversational prose responding to the learner.")
    blocks: List[ContentBlock] = Field(default_factory=list, description="Optional. Any diagrams, examples, or interactive blocks to include in the reply.")

class CheckpointItemDraft(BaseModel):
    id: str = Field(description="Unique string ID for the item")
    type: str = Field(description="e.g. multiple_choice, free_response, etc.")
    question: str
    options: Optional[List[str]] = None
    concept_ids: List[UUID]

class CheckpointDraft(BaseModel):
    items: List[CheckpointItemDraft]

class MasteryDeltaDraft(BaseModel):
    concept_id: UUID
    delta: float

class ItemFeedbackDraft(BaseModel):
    item_id: str
    correct: bool
    explanation: str

class EvaluationDraft(BaseModel):
    score: float = Field(description="Overall score from 0.0 to 1.0")
    mastery_deltas: List[MasteryDeltaDraft]
    feedback: List[ItemFeedbackDraft]


# -------------------------
# Adaptor Schemas
# -------------------------

class PlanChange(BaseModel):
    module_id: Optional[UUID] = Field(default=None, description="The module this change affects, if any.")
    lesson_id: Optional[UUID] = Field(default=None, description="The lesson this change affects, if any.")
    change_type: Literal["insert", "delete", "move", "update"] = Field(description="The type of change.")
    details: str = Field(description="JSON string representation of details. Can include new_module, new_lesson, etc.")

class AdaptationDecision(BaseModel):
    trigger: Literal["struggling", "stuck", "racing", "stalled", "decaying"] = Field(description="The trigger that fired.")
    action: Literal["insert_prerequisite", "slow_pace", "reexplain_concept", "compress_forward", "reorder", "extend_timeline", "no_op"] = Field(description="What to do.")
    reason: str = Field(min_length=60, description="Specific reason shown to the learner. Must name the concept, cite evidence, and explain consequence. Do not use generic phrases.")
    timeline_impact: str = Field(min_length=20, description="Concrete timeline impact shown to learner. E.g. 'adds ~25 min; still on track for your 12 Oct deadline'")
    changes: List[PlanChange] = Field(description="The specific plan changes.")
