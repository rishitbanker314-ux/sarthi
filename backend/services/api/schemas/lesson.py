from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ReexplainRequest(BaseModel):
    block_id: UUID
    reason: Optional[str] = None
