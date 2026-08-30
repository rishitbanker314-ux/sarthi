import asyncio
import json
import logging
from typing import AsyncGenerator, Any
from fastapi.responses import StreamingResponse
from starlette.requests import Request
from services.api.errors import AppError

logger = logging.getLogger(__name__)

async def _run_generator(q: asyncio.Queue, generator: AsyncGenerator[tuple[str, Any], None]):
    try:
        async for event, data in generator:
            await q.put((event, data))
            if event in ("done", "error"):
                break
        await q.put(None)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        await q.put(e)

async def stream_with_heartbeat(
    request: Request,
    generator: AsyncGenerator[tuple[str, Any], None],
    heartbeat_interval: float = 15.0
) -> AsyncGenerator[str, None]:
    
    q: asyncio.Queue = asyncio.Queue()
    gen_task = asyncio.create_task(_run_generator(q, generator))
    terminal_emitted = False
    
    def format_event(event: str, data: Any) -> str:
        data_str = json.dumps(data) if isinstance(data, (dict, list, bool, int, float)) else str(data)
        return f"event: {event}\ndata: {data_str}\n\n"

    disconnect_task = asyncio.create_task(request.is_disconnected())
    
    try:
        while True:
            if disconnect_task.done() and disconnect_task.result() is True:
                logger.info("Client disconnected")
                gen_task.cancel()
                break

            q_task = asyncio.create_task(q.get())

            done, pending = await asyncio.wait(
                [disconnect_task, q_task],
                timeout=heartbeat_interval,
                return_when=asyncio.FIRST_COMPLETED
            )

            if disconnect_task in done:
                if disconnect_task.result() is True:
                    logger.info("Client disconnected")
                    q_task.cancel()
                    gen_task.cancel()
                    break
                else:
                    # Request is still connected, recreate task for next loop
                    disconnect_task = asyncio.create_task(request.is_disconnected())
            
            if q_task in done:
                item = q_task.result()
                if item is None:
                    break
                elif isinstance(item, Exception):
                    e = item
                    logger.exception("Exception in SSE generator")
                    if isinstance(e, AppError):
                        err_data = {
                            "code": getattr(e, "code", "INTERNAL_ERROR"),
                            "message": e.message if hasattr(e, 'message') else str(e),
                            "retryable": getattr(e, "retryable", False),
                            "details": getattr(e, "details", {})
                        }
                    else:
                        err_data = {
                            "code": "INTERNAL_ERROR",
                            "message": "Something went wrong on our end.",
                            "retryable": True,
                            "details": {}
                        }
                    yield format_event("error", err_data)
                    terminal_emitted = True
                    break
                else:
                    event, data = item
                    if event not in ("token", "block", "tool", "done", "error"):
                        logger.warning(f"Invalid SSE event type emitted: {event}")
                    
                    yield format_event(event, data)
                    
                    if event in ("done", "error"):
                        terminal_emitted = True
                        break
            else:
                q_task.cancel()
                yield ": ping\n\n"
                
    finally:
        if not terminal_emitted:
            yield format_event("error", {
                "code": "STREAM_ENDED_UNEXPECTEDLY",
                "message": "The stream ended without a terminal event.",
                "retryable": True,
                "details": {}
            })
            
        if not disconnect_task.done():
            disconnect_task.cancel()
        if not gen_task.done():
            gen_task.cancel()

def sse_response(request: Request, generator: AsyncGenerator[tuple[str, Any], None]) -> StreamingResponse:
    return StreamingResponse(
        stream_with_heartbeat(request, generator),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
