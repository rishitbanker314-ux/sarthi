import asyncio
from httpx import AsyncClient, ASGITransport
from services.api.main import app
async def main():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/me")
        print(f"Status Code: {r.status_code}")
        print(f"Body: {r.text}")
asyncio.run(main())
