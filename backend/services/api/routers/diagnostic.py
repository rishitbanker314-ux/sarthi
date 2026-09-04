import uuid
from fastapi import APIRouter, Depends, Request
from services.api.rate_limiter import limiter
from sqlalchemy.ext.asyncio import AsyncSession
from services.api.db import get_session
from services.api.auth.dependencies import get_current_user, CurrentUser
from services.api.schemas.diagnostic import DiagnosticActionResponse, DiagnosticAnswerRequest
from services.api.schemas.learner_profile import LearnerProfileResponse
from services.api.services import diagnostic

router = APIRouter(prefix="/api/v1/diagnostic", tags=["Diagnostic"])

@router.post("/sessions", response_model=DiagnosticActionResponse, status_code=200)
async def start_diagnostic_session(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await diagnostic.start_session(current_user.id, db)

@router.get("/sessions/{session_id}", response_model=DiagnosticActionResponse, status_code=200)
async def resume_diagnostic_session(
    session_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await diagnostic.resume_session(session_id, current_user.id, db)

@router.post("/sessions/{session_id}/answer", response_model=DiagnosticActionResponse, status_code=200)
@limiter.limit("10/minute")
async def answer_diagnostic_question(
    session_id: uuid.UUID,
    request_body: DiagnosticAnswerRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await diagnostic.answer_question(session_id, current_user.id, request_body.answer, db)

@router.post("/sessions/{session_id}/complete", response_model=LearnerProfileResponse, status_code=200)
async def complete_diagnostic_session(
    session_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await diagnostic.complete_session(session_id, current_user.id, db)
