import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch, AsyncMock

from services.api.models.diagnostic_session import DiagnosticSession
from services.api.models.learner_profile import LearnerProfile
from services.api.models.enums import DiagnosticStatus
from services.api.schemas.diagnostic import NextQuestionSchema
from services.agents.schemas import DiagnosticResponse, NextQuestion, ProfileDraft, AccessibilityOptions

@pytest.fixture
def mock_get_next_action():
    async def fake_get_next_action(transcript):
        if len(transcript) < 4:
            return DiagnosticResponse(
                complete=False,
                questions=[NextQuestion(question_text=f"Question {len(transcript)}", question_type="short_text")]
            )
        else:
            return DiagnosticResponse(
                complete=True,
                profile_draft=ProfileDraft(
                    prior_knowledge="solid", pace="fast", representation_pref="abstract_first",
                    scaffolding_pref="guided_discovery", depth_pref="depth_mastery", motivation="career",
                    session_minutes=60, language="en", accessibility=AccessibilityOptions()
                )
            )
            
    with patch("services.api.services.diagnostic.get_next_action", side_effect=fake_get_next_action) as m:
        yield m

@pytest.mark.asyncio
async def test_diagnostic_happy_path(client: AsyncClient, token_headers: dict, db_session: AsyncSession, mock_get_next_action):
    # Ensure user exists
    await client.get("/api/v1/me", headers=token_headers)
    
    # 1. Start Session
    res_start = await client.post("/api/v1/diagnostic/sessions", headers=token_headers)
    assert res_start.status_code == 200
    start_data = res_start.json()
    assert start_data["status"] == "started"
    assert start_data["complete"] is False
    assert "Question 0" in start_data["question"]["question_text"]
    
    session_id = start_data["id"]
    
    # 2. Resume Session
    res_resume = await client.get(f"/api/v1/diagnostic/sessions/{session_id}", headers=token_headers)
    assert res_resume.status_code == 200
    resume_data = res_resume.json()
    assert resume_data["question"]["question_text"] == start_data["question"]["question_text"]
    
    # 3. Answer questions until complete
    res_ans1 = await client.post(f"/api/v1/diagnostic/sessions/{session_id}/answer", json={"answer": "Ans 1"}, headers=token_headers)
    assert res_ans1.status_code == 200
    ans1_data = res_ans1.json()
    assert not ans1_data["complete"]
    assert "Question 2" in ans1_data["question"]["question_text"] # len is 2 after appending learner answer
    
    res_ans2 = await client.post(f"/api/v1/diagnostic/sessions/{session_id}/answer", json={"answer": "Ans 2"}, headers=token_headers)
    assert res_ans2.status_code == 200
    ans2_data = res_ans2.json()
    assert ans2_data["complete"] is True
    assert ans2_data["question"] is None
    
    # 4. Try to answer again -> 409
    res_ans_err = await client.post(f"/api/v1/diagnostic/sessions/{session_id}/answer", json={"answer": "Ans 3"}, headers=token_headers)
    assert res_ans_err.status_code == 409
    assert res_ans_err.json()["error"]["code"] == "DIAGNOSTIC_ALREADY_COMPLETE"
    
    # 5. Complete Session -> creates profile
    res_comp1 = await client.post(f"/api/v1/diagnostic/sessions/{session_id}/complete", headers=token_headers)
    assert res_comp1.status_code == 200
    prof1_data = res_comp1.json()
    assert prof1_data["prior_knowledge"]["_global"] == "solid"
    
    # 6. Complete Session again -> idempotent
    res_comp2 = await client.post(f"/api/v1/diagnostic/sessions/{session_id}/complete", headers=token_headers)
    assert res_comp2.status_code == 200
    assert res_comp2.json()["id"] == prof1_data["id"]

@pytest.mark.asyncio
async def test_diagnostic_other_user(client: AsyncClient, token_headers: dict, db_session: AsyncSession):
    # This tests that accessing a non-existent or other user's session returns 404
    fake_id = str(uuid.uuid4())
    res = await client.get(f"/api/v1/diagnostic/sessions/{fake_id}", headers=token_headers)
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"
