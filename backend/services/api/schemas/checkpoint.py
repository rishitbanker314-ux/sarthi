from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class CheckpointItem(BaseModel):
    id: str
    type: str # e.g. "multiple_choice", "free_response", "code_snippet"
    question: str
    options: Optional[List[str]] = None
    concept_ids: List[UUID]

class CheckpointResponse(BaseModel):
    id: UUID
    lesson_id: UUID
    items: List[CheckpointItem]
    created_at: datetime

class CheckpointSubmitRequest(BaseModel):
    responses: Dict[str, Any] # mapping from item id to user's response

class MasteryDelta(BaseModel):
    concept_id: UUID
    delta: float

class ItemFeedback(BaseModel):
    item_id: str
    correct: bool
    explanation: str

class CheckpointAttemptResponse(BaseModel):
    id: UUID
    score: float
    mastery_deltas: List[MasteryDelta]
    feedback: List[ItemFeedback]
    submitted_at: datetime
