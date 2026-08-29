import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import APIRouter, Depends
from services.api.main import app
from services.api.schemas.pagination import PaginationParams, SortParams, PaginatedResponse

dummy_router = APIRouter()

@dummy_router.get("/test/items", response_model=PaginatedResponse[str])
async def get_items(
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends()
):
    # Dummy implementation for testing
    items = ["item1", "item2", "item3"]
    
    # Normally we would apply sorting and pagination to a query
    # Here we just reflect it back to verify the contract
    has_more = pagination.page * pagination.size < 100 # arbitrary logic for test
    
    return PaginatedResponse(
        data=items,
        total=100,
        page=pagination.page,
        size=pagination.size,
        has_more=has_more
    )

app.include_router(dummy_router)

@pytest.mark.asyncio
async def test_pagination_default():
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        response = await client.get("/test/items")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 50
        assert data["total"] == 100
        assert data["has_more"] is True
        assert data["data"] == ["item1", "item2", "item3"]

@pytest.mark.asyncio
async def test_pagination_custom():
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        response = await client.get("/test/items?page=2&size=10&sort_by=name&sort_desc=true")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["size"] == 10
        assert data["total"] == 100
        assert data["has_more"] is True
        assert data["data"] == ["item1", "item2", "item3"]

@pytest.mark.asyncio
async def test_pagination_invalid():
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        response = await client.get("/test/items?page=0") # Invalid page (ge=1)
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
