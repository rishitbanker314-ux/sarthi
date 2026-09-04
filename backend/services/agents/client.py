import json
import os
import hashlib
import asyncio
from pathlib import Path
from google import genai
from google.genai import types
from pydantic import BaseModel

from services.api.config import get_settings
from services.agents.rate_pacing import wait_for_tier

# Initialize the Gemini client lazily or once
_client = None

# Global semaphore for concurrency cap
_semaphore = None

def get_gemini_client(api_key: str = None):
    global _client
    if _client is None or api_key:
        settings = get_settings()
        key_to_use = api_key or settings.gemini_api_key
        if key_to_use:
            _client = genai.Client(api_key=key_to_use)
        else:
            # For testing with fake keys or DEMO_MODE
            _client = genai.Client(api_key="fake-key-for-tests")
    return _client

def get_semaphore():
    global _semaphore
    if _semaphore is None:
        settings = get_settings()
        _semaphore = asyncio.Semaphore(settings.max_concurrent_users)
    return _semaphore

def _get_fixture_path(agent_name: str, context: dict) -> Path:
    base_dir = Path(__file__).parent.parent.parent / "fixtures" / "demo"
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create deterministic hash of inputs
    # Sort keys to ensure consistent hashing
    ctx_str = json.dumps(context, sort_keys=True)
    ctx_hash = hashlib.md5(ctx_str.encode("utf-8")).hexdigest()[:8]
    
    return base_dir / f"{agent_name}_{ctx_hash}.json"

def _get_default_fixture_path(agent_name: str) -> Path:
    base_dir = Path(__file__).parent.parent.parent / "fixtures" / "demo"
    return base_dir / f"{agent_name}_default.json"

class _FakeResponse:
    def __init__(self, parsed: BaseModel):
        self.parsed = parsed
        self.usage_metadata = types.GenerateContentResponseUsageMetadata(
            prompt_token_count=1200,
            candidates_token_count=450,
            total_token_count=1650
        )

async def generate_content_async(
    agent_name: str,
    model_id: str,
    prompt: str,
    context: dict,
    output_model: type[BaseModel],
    use_schema: bool = True,
    api_key: str | None = None,
    pacing_timeout: float | None = None,
    progress_callback = None,
    **kwargs
) -> any:
    """
    Wraps the Gemini call, handles DEMO_MODE (loading fixtures),
    and RECORD_FIXTURES (saving responses).
    Uses a specific API key if provided via kwargs.
    """
    settings = get_settings()
    api_key = api_key or kwargs.get("api_key", None)
    
    if settings.demo_mode:
        # Load from fixture
        path = _get_fixture_path(agent_name, context)
        if not path.exists():
            path = _get_default_fixture_path(agent_name)
            if not path.exists():
                raise FileNotFoundError(f"No fixture found for agent '{agent_name}'")
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Parse into the output model to simulate what Gemini's SDK does
        parsed = output_model.model_validate(data)
        return _FakeResponse(parsed=parsed)
    
    # Real network call
    client = get_gemini_client(api_key)
    
    if use_schema:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=output_model,
            temperature=0.0
        )
    else:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0
        )
    
    semaphore = get_semaphore()
    async with semaphore:
        await wait_for_tier(model_id, timeout=pacing_timeout, progress_callback=progress_callback)
        response = await client.aio.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config
        )
        
    # If not using schema, we must parse the text manually
    if not use_schema and response.text:
        text = response.text
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        
        try:
            parsed = output_model.model_validate_json(text.strip())
            response.parsed = parsed
        except Exception as e:
            # Re-raise to be caught by the retry loop in base.py
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse text: {text}")
    
    # Record fixture if needed
    if settings.record_fixtures and response.parsed:
        path = _get_fixture_path(agent_name, context)
        # Convert pydantic model to dict
        data = response.parsed.model_dump()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
    return response
