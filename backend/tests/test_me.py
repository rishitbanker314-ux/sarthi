import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from services.api.models.user import User

@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    """Test that missing token returns 401."""
    response = await client.get("/api/v1/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_me_creates_user(client: AsyncClient, token_headers: dict, db_session: AsyncSession):
    """Test that first call to /me creates the user lazily."""
    # First call
    response1 = await client.get("/api/v1/me", headers=token_headers)
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["email"] == "test@example.com"
    assert data1["has_learner_profile"] is False
    assert data1["profile_version"] is None
    
    # Verify in DB
    result = await db_session.execute(select(User).where(User.email == "test@example.com"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert str(user.id) == data1["id"]
    
    # Second call
    response2 = await client.get("/api/v1/me", headers=token_headers)
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["id"] == data1["id"]
    
    # Verify no duplicates
    result = await db_session.execute(select(User).where(User.email == "test@example.com"))
    users = result.scalars().all()
    assert len(users) == 1
