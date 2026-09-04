import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from services.api.errors import NotFoundError, ConflictError
from services.api.models.diagnostic_session import DiagnosticSession
from services.api.models.learner_profile import LearnerProfile
from services.api.models.enums import DiagnosticStatus, Pace, RepresentationPref, ScaffoldingPref, DepthPref, Motivation
from services.api.schemas.diagnostic import DiagnosticActionResponse, NextQuestionSchema, DiagnosticProgress
from services.api.schemas.learner_profile import LearnerProfileResponse
from services.agents.diagnostician import get_next_action

async def get_diagnostic_session(session_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> DiagnosticSession:
    result = await db.execute(
        select(DiagnosticSession).where(
            DiagnosticSession.id == session_id,
            DiagnosticSession.user_id == user_id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundError("Diagnostic session not found.")
    return session

async def start_session(user_id: uuid.UUID, db: AsyncSession) -> DiagnosticActionResponse:
    # 1. Start agent with empty transcript
    action = await get_next_action([])
    
    # 2. Add question to transcript and queue remaining
    transcript = []
    q_schema = None
    if not action.complete and action.questions:
        q = action.questions[0]
        transcript.append({"agent": q.question_text})
        
        q_schema = NextQuestionSchema(
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options
        )
        
        remaining = [qq.model_dump() for qq in action.questions[1:]]
        if remaining:
            transcript.append({"queue": remaining})
    
    # 3. Create session
    session = DiagnosticSession(
        user_id=user_id,
        status=DiagnosticStatus.started,
        transcript=transcript,
        derived_profile=None
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return DiagnosticActionResponse(
        id=session.id,
        status=session.status,
        complete=action.complete,
        question=q_schema,
        progress=DiagnosticProgress(answered=0)
    )

async def resume_session(session_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> DiagnosticActionResponse:
    session = await get_diagnostic_session(session_id, user_id, db)
    
    is_complete = session.status == DiagnosticStatus.completed
    q_schema = None
    answered = len([x for x in session.transcript if "learner" in x])

    if not is_complete:
        # Find the last agent question
        last_q = None
        for item in reversed(session.transcript):
            if "agent" in item:
                last_q = item["agent"]
                break
        
        if last_q:
            q_schema = NextQuestionSchema(
                question_text=last_q,
                question_type="short_text"
            )
            
    return DiagnosticActionResponse(
        id=session.id,
        status=session.status,
        complete=is_complete,
        question=q_schema,
        progress=DiagnosticProgress(answered=answered)
    )

async def answer_question(session_id: uuid.UUID, user_id: uuid.UUID, answer: str, db: AsyncSession) -> DiagnosticActionResponse:
    session = await get_diagnostic_session(session_id, user_id, db)
    
    if session.status == DiagnosticStatus.completed:
        raise ConflictError("Diagnostic session is already complete.", code="DIAGNOSTIC_ALREADY_COMPLETE")
        
    # Append the answer to the last interaction
    new_transcript = list(session.transcript)
    new_transcript.append({"learner": answer})
    
    q_schema = None
    complete = False
    derived_profile = None
    
    # Check if we have items in the queue
    queue_idx = -1
    for i, item in enumerate(new_transcript):
        if "queue" in item:
            queue_idx = i
            break
            
    if queue_idx >= 0 and new_transcript[queue_idx]["queue"]:
        queue = new_transcript[queue_idx]["queue"]
        next_q = queue.pop(0)
        new_transcript.append({"agent": next_q["question_text"]})
        q_schema = NextQuestionSchema(**next_q)
        
        if queue:
            new_transcript.append({"queue": queue})
            
        del new_transcript[queue_idx] # Remove old queue
    else:
        # Queue is empty, call agent
        if queue_idx >= 0:
            del new_transcript[queue_idx]
            
        action = await get_next_action(new_transcript)
        complete = action.complete
        if action.profile_draft:
            derived_profile = action.profile_draft.model_dump(mode="json")
            
        if not action.complete and action.questions:
            q = action.questions[0]
            new_transcript.append({"agent": q.question_text})
            q_schema = NextQuestionSchema(
                question_text=q.question_text,
                question_type=q.question_type,
                options=q.options
            )
            
            remaining = [qq.model_dump() for qq in action.questions[1:]]
            if remaining:
                new_transcript.append({"queue": remaining})
        
    session.transcript = new_transcript
    
    if complete:
        session.status = DiagnosticStatus.completed
        session.completed_at = func.now()
        session.derived_profile = derived_profile or {}
        
    await db.commit()
    await db.refresh(session)
    
    answered = len([x for x in session.transcript if "learner" in x])
    return DiagnosticActionResponse(
        id=session.id,
        status=session.status,
        complete=complete,
        question=q_schema,
        progress=DiagnosticProgress(answered=answered)
    )

async def complete_session(session_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> LearnerProfileResponse:
    session = await get_diagnostic_session(session_id, user_id, db)
    
    if session.status != DiagnosticStatus.completed:
        raise ConflictError("Session is not complete yet.")
        
    # Check if a profile_version=1 already exists
    result = await db.execute(
        select(LearnerProfile).where(
            LearnerProfile.user_id == user_id,
            LearnerProfile.profile_version == 1
        )
    )
    existing_profile = result.scalar_one_or_none()
    if existing_profile:
        return LearnerProfileResponse.model_validate(existing_profile)
        
    # Create the profile
    derived = session.derived_profile or {}
    
    profile = LearnerProfile(
        user_id=user_id,
        profile_version=1,
        prior_knowledge={"_global": derived.get("prior_knowledge", "shaky")},
        pace=Pace(derived.get("pace", "standard")),
        representation_pref=RepresentationPref(derived.get("representation_pref", "concrete_first")),
        scaffolding_pref=ScaffoldingPref(derived.get("scaffolding_pref", "worked_examples")),
        depth_pref=DepthPref(derived.get("depth_pref", "breadth_survey")),
        motivation=Motivation(derived.get("motivation", "curiosity")),
        session_minutes=derived.get("session_minutes", 30),
        language=derived.get("language", "en"),
        accessibility=derived.get("accessibility", {})
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    return LearnerProfileResponse.model_validate(profile)
