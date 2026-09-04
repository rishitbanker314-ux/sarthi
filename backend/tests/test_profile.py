import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.models.learner_profile import LearnerProfile
from services.api.models.enums import Pace

@pytest.mark.asyncio
async def test_get_profile_not_found(client: AsyncClient, token_headers: dict):
    # Ensure user exists
    await client.get("/api/v1/me", headers=token_headers)
    
    # Check profile returns 404
    res = await client.get("/api/v1/profile/learner", headers=token_headers)
    assert res.status_code == 404

@pytest.mark.asyncio
async def test_profile_update(client: AsyncClient, token_headers: dict, db_session: AsyncSession):
    # Ensure user exists
    await client.get("/api/v1/me", headers=token_headers)
    
    # We must insert a profile directly to test PATCH easily
    from services.api.models.enums import RepresentationPref, ScaffoldingPref, DepthPref, Motivation
    user_id_str = (await client.get("/api/v1/me", headers=token_headers)).json()["id"]
    uid = uuid.UUID(user_id_str)
    
    profile = LearnerProfile(
        user_id=uid,
        profile_version=1,
        prior_knowledge={"_global": "shaky"},
        pace=Pace.standard,
        representation_pref=RepresentationPref.concrete_first,
        scaffolding_pref=ScaffoldingPref.guided_discovery,
        depth_pref=DepthPref.breadth_survey,
        motivation=Motivation.curiosity,
        session_minutes=30,
        language="en",
        accessibility={}
    )
    db_session.add(profile)
    await db_session.commit()
    
    # 1. GET profile
    res_get = await client.get("/api/v1/profile/learner", headers=token_headers)
    assert res_get.status_code == 200
    get_data = res_get.json()
    assert get_data["profile_version"] == 1
    assert get_data["pace"] == "standard"
    
    # 2. PATCH profile
    res_patch = await client.patch("/api/v1/profile/learner", headers=token_headers, json={"pace": "fast"})
    assert res_patch.status_code == 200
    patch_data = res_patch.json()
    assert patch_data["profile_version"] == 2
    assert patch_data["pace"] == "fast"
    
    # The rest should be unchanged
    assert patch_data["prior_knowledge"] == get_data["prior_knowledge"]
    assert patch_data["language"] == "en"
    
    # 3. GET me checks
    res_me = await client.get("/api/v1/me", headers=token_headers)
    assert res_me.status_code == 200
    me_data = res_me.json()
    assert me_data["has_learner_profile"] is True
    assert me_data["profile_version"] == 2
