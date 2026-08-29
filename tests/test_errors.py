import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import APIRouter
from pydantic import BaseModel
from services.api.main import app
from services.api.errors import NotFoundError

dummy_router = APIRouter()

@dummy_router.get("/test/app-error")
async def trigger_app_error():
    raise NotFoundError("Test resource not found")

class DummyModel(BaseModel):
    name: str

@dummy_router.post("/test/validation-error")
async def trigger_validation_error(model: DummyModel):
    return model

@dummy_router.get("/test/unhandled")
async def trigger_unhandled():
    1 / 0

app.include_router(dummy_router)

@pytest.mark.asyncio
async def test_app_error():
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        response = await client.get("/test/app-error")
        assert response.status_code == 404
        assert "X-Request-ID" in response.headers
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
        assert data["error"]["message"] == "Test resource not found"
        assert data["error"]["retryable"] is False
        assert data["error"]["details"] == {}

@pytest.mark.asyncio
async def test_validation_error():
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        response = await client.post("/test/validation-error", json={"invalid": "data"})
        assert response.status_code == 422
        assert "X-Request-ID" in response.headers
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["error"]["message"] == "Invalid request parameters"
        assert data["error"]["retryable"] is False
        assert "errors" in data["error"]["details"]

@pytest.mark.asyncio
async def test_http_exception():
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        # Route doesn't exist
        response = await client.get("/does/not/exist")
        assert response.status_code == 404
        assert "X-Request-ID" in response.headers
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "HTTP_ERROR"
        assert data["error"]["message"] == "Not Found"
        assert data["error"]["retryable"] is False

@pytest.mark.asyncio
async def test_unhandled_exception():
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        response = await client.get("/test/unhandled")
        assert response.status_code == 500
        assert "X-Request-ID" in response.headers
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert data["error"]["message"] == "Something went wrong on our end."
        assert data["error"]["retryable"] is True
        assert data["error"]["details"] == {}
        # Ensure traceback is not leaked
        assert "ZeroDivisionError" not in response.text
