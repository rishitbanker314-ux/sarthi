import asyncio
import pytest
import json
from fastapi import FastAPI, Request
from httpx import AsyncClient, ASGITransport
from services.api.sse import sse_response
from services.api.errors import AppError

app = FastAPI()

async def normal_stream():
    yield "token", {"text": "hello"}
    yield "block", {"id": "1", "type": "text"}
    yield "done", {"message_id": "123", "block_count": 1, "usage": {}}

@app.get("/normal")
async def normal_route(request: Request):
    return sse_response(request, normal_stream())

async def raising_stream():
    yield "token", {"text": "about to raise"}
    raise ValueError("Test error")

@app.get("/raising")
async def raising_route(request: Request):
    return sse_response(request, raising_stream())

async def app_error_stream():
    yield "token", {"text": "about to raise app error"}
    raise AppError(code="TEST_ERR", message="Test message", http_status=400, retryable=False, details={"foo": "bar"})

@app.get("/app_error")
async def app_error_route(request: Request):
    return sse_response(request, app_error_stream())

async def no_terminal_stream():
    yield "token", {"text": "just tokens"}
    yield "token", {"text": "and then I stop"}

@app.get("/no_terminal")
async def no_terminal_route(request: Request):
    return sse_response(request, no_terminal_stream())

async def slow_stream():
    yield "token", {"text": "start"}
    await asyncio.sleep(0.3)
    yield "done", {}

@app.get("/slow")
async def slow_route(request: Request):
    # Pass a tiny heartbeat interval to trigger heartbeats quickly
    from services.api.sse import stream_with_heartbeat
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        stream_with_heartbeat(request, slow_stream(), heartbeat_interval=0.1),
        media_type="text/event-stream"
    )

# 1. a normal stream ends with exactly one `done`
@pytest.mark.asyncio
async def test_normal_stream():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/normal")
        assert response.status_code == 200
        content = response.text
        events = content.strip().split("\n\n")
        assert "event: token" in events[0]
        assert "event: block" in events[1]
        assert "event: done" in events[2]
        assert len(events) == 3

# 2. a generator that raises ends with exactly one `error` and no `done`
@pytest.mark.asyncio
async def test_raising_stream():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/raising")
        content = response.text
        events = content.strip().split("\n\n")
        assert "event: token" in events[0]
        assert "event: error" in events[1]
        
        # Check error format
        error_data = json.loads(events[1].replace("event: error\ndata: ", ""))
        assert error_data["code"] == "INTERNAL_ERROR"
        assert error_data["retryable"] is True
        assert len(events) == 2

@pytest.mark.asyncio
async def test_app_error_stream():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/app_error")
        content = response.text
        events = content.strip().split("\n\n")
        
        error_data = json.loads(events[1].replace("event: error\ndata: ", ""))
        assert error_data["code"] == "TEST_ERR"
        assert error_data["message"] == "Test message"
        assert error_data["retryable"] is False
        assert error_data["details"] == {"foo": "bar"}

# 3. a generator that returns without a terminal event still ends with `error`
@pytest.mark.asyncio
async def test_no_terminal_stream():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/no_terminal")
        content = response.text
        events = content.strip().split("\n\n")
        assert "event: token" in events[0]
        assert "event: token" in events[1]
        assert "event: error" in events[2]
        
        error_data = json.loads(events[2].replace("event: error\ndata: ", ""))
        assert error_data["code"] == "STREAM_ENDED_UNEXPECTEDLY"
        assert len(events) == 3

# 4. heartbeats appear during a slow generator
@pytest.mark.asyncio
async def test_slow_stream():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/slow")
        content = response.text
        events = content.strip().split("\n\n")
        assert "event: token" in events[0]
        assert ": ping" in events[1]
        assert "event: done" in events[-1]

# 5. disconnect cancels the inner task
@pytest.mark.asyncio
async def test_disconnect_cancels_task():
    # It's a bit tricky to test client disconnect cleanly via httpx's ASGITransport
    # but we can simulate it with a test request.
    task_cancelled = False
    
    async def infinite_stream():
        nonlocal task_cancelled
        try:
            while True:
                yield "token", {"text": "wait"}
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            task_cancelled = True
            raise

    # We will test the disconnect handling by creating a dummy request that returns True for is_disconnected
    from services.api.sse import stream_with_heartbeat
    from unittest.mock import AsyncMock
    
    mock_request = AsyncMock()
    # It starts connected, then disconnects
    mock_request.is_disconnected.side_effect = [False, False, True]
    
    streamer = stream_with_heartbeat(mock_request, infinite_stream(), heartbeat_interval=0.05)
    
    # Run the streamer manually
    async for item in streamer:
        pass
        
    await asyncio.sleep(0.05)
    assert task_cancelled is True
