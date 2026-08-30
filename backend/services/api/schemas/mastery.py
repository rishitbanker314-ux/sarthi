from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from decimal import Decimal

class MasteryStateResponse(BaseModel):
    id: UUID
    user_id: UUID
    concept_id: UUID
    score: Decimal
    confidence: Decimal
    attempts: int
    created_at: datetime
    last_seen_at: datetime
