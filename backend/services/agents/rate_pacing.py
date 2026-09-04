import asyncio
import time

class CapacityError(Exception):
    pass

class TierLimiter:
    def __init__(self, rpm: int):
        self.interval = 60.0 / rpm if rpm > 0 else 0
        self.last_call = 0.0
        self.lock = asyncio.Lock()

    async def wait(self, timeout: float | None = None, progress_callback = None):
        if self.interval == 0:
            return
            
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_call
            wait_time = self.interval - elapsed
            if wait_time > 0:
                if timeout is not None and wait_time > timeout:
                    raise CapacityError("Capacity wait exceeded timeout")
                if progress_callback:
                    await progress_callback("Waiting for capacity")
                await asyncio.sleep(wait_time)
            self.last_call = time.time()

# Free tier limits based on https://ai.google.dev/gemini-api/docs/rate-limits
# Flash: 15 RPM
# Pro: 2 RPM
flash_limiter = TierLimiter(15)
pro_limiter = TierLimiter(2)

async def wait_for_tier(model_id: str, timeout: float | None = None, progress_callback = None):
    """Wait according to the model's tier limit."""
    if "pro" in model_id.lower():
        await pro_limiter.wait(timeout=timeout, progress_callback=progress_callback)
    else:
        await flash_limiter.wait(timeout=timeout, progress_callback=progress_callback)
