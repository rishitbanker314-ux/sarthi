import uuid
from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, Field

class GoalCreate(BaseModel):
    raw_input: str = Field(..., min_length=10, description="The raw natural language input describing the goal.")

class GoalResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    raw_input: str
    normalized_topic: str
    target_level: str
    deadline: Optional[date]
    motivation_hint: Optional[str]
    is_educational: bool
    clarification_needed: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class GoalUpdate(BaseModel):
    normalized_topic: Optional[str] = Field(None, description="Corrected topic.")
    target_level: Optional[Literal["beginner", "intermediate", "advanced"]] = Field(None, description="Corrected target level.")
    deadline: Optional[date] = Field(None, description="Corrected deadline.")
