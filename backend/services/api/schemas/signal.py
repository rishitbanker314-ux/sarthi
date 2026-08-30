from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.api.models.enums import SignalType

class SignalCreate(BaseModel):
    block_id: Optional[UUID] = None
    type: SignalType
    value: Dict[str, Any] = {}

class SignalResponse(BaseModel):
    id: UUID
    user_id: UUID
    lesson_id: Optional[UUID]
    block_id: Optional[UUID]
    type: SignalType
    value: Dict[str, Any]
    created_at: datetime
