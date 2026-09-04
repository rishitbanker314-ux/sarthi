from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from services.api.models.enums import MessageRole

class TutorMessageRequest(BaseModel):
    lesson_id: UUID
    thread_id: Optional[UUID] = None
    content: str
    context_block_id: Optional[UUID] = None

class TutorMessageResponse(BaseModel):
    id: UUID
    thread_id: UUID
    role: MessageRole
    content: str
    blocks: Optional[dict] = None
    created_at: datetime
    
class TutorThreadResponse(BaseModel):
    id: UUID
    lesson_id: UUID
    messages: List[TutorMessageResponse]
