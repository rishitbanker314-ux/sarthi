import uuid
from typing import Optional
from pydantic import BaseModel, Field

from services.api.models.enums import DiagnosticStatus

class NextQuestionSchema(BaseModel):
    question_text: str
    question_type: str
    options: Optional[list[str]] = None

class DiagnosticProgress(BaseModel):
    answered: int
    estimated_total: int = 10

class DiagnosticActionResponse(BaseModel):
    id: uuid.UUID = Field(description="The session ID")
    status: DiagnosticStatus = Field(description="The status of the diagnostic session")
    complete: bool = Field(description="True if the diagnostic is complete and ready to be finalized")
    question: Optional[NextQuestionSchema] = Field(default=None, description="The next question to ask the user")
    progress: Optional[DiagnosticProgress] = Field(default=None, description="Progress indicator")

class DiagnosticAnswerRequest(BaseModel):
    answer: str
