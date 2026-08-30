import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class LessonResponse(BaseModel):
    id: uuid.UUID
    module_id: uuid.UUID
    order_index: int
    title: str
    objective: str
    concept_ids: List[uuid.UUID]
    est_minutes: int
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ModuleResponse(BaseModel):
    id: uuid.UUID
    plan_id: uuid.UUID
    order_index: int
    title: str
    objective: str
    rationale: str
    est_minutes: int
    status: str
    lessons: List[LessonResponse]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PlanResponse(BaseModel):
    id: uuid.UUID
    goal_id: uuid.UUID
    version: int
    title: str
    rationale: str
    profile_version: int
    status: str
    modules: List[ModuleResponse]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
