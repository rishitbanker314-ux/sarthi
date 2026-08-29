import pytest
from httpx import AsyncClient, ASGITransport
from services.api.main import app
from unittest.mock import patch

@pytest.mark.asyncio
async def test_health():
    # We use mock to simulate the db session so it doesn't try to connect to a non-existent database during isolated tests
    with patch("services.api.routers.health.AsyncSession.execute") as mock_execute:
        # DB will be mocked to return ok for testing the endpoint logic itself
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["db"] == "ok"
            assert "version" in data
            assert "env" in data
