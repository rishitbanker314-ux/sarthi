import asyncio
import httpx
import uuid

async def run():
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get("http://127.0.0.1:8001/health/usage")
        print(resp.status_code)
        print(resp.json())

asyncio.run(run())
