import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, ConfigDict

from services.api.models.enums import JobKind, JobStatus

class PlanGenerationResult(BaseModel):
    plan_id: uuid.UUID

class ReplanResult(BaseModel):
    plan_id: uuid.UUID
    adaptation_event_id: uuid.UUID

class JobError(BaseModel):
    code: str
    message: str
    retryable: bool
    details: Dict[str, Any] = Field(default_factory=dict)

class JobResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    kind: JobKind
    status: JobStatus
    progress: int
    progress_message: Optional[str] = None
    result: Union[PlanGenerationResult, ReplanResult, None] = None
    error: Optional[JobError] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
