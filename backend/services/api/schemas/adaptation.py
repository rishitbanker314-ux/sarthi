from typing import List, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from services.api.models.enums import AdaptationTrigger, AdaptationAction

class AdaptationRespondRequest(BaseModel):
    accepted: bool

class AdaptationEventResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime
    plan_id: uuid.UUID
    trigger: AdaptationTrigger
    action: AdaptationAction
    reason: str
    timeline_impact: str
    before: dict
    after: dict
    accepted: Optional[bool]
    
    model_config = ConfigDict(from_attributes=True)

class AdaptationListResponse(BaseModel):
    items: List[AdaptationEventResponse]
    total: int
