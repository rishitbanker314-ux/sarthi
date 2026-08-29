import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class MeResponse(BaseModel):
    id: uuid.UUID
    email: str
    display_name: Optional[str]
    locale: str
    created_at: datetime
    
    # TODO(Phase 1 Task 4): Wire up the learner profile checks
    has_learner_profile: bool = False
    profile_version: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
