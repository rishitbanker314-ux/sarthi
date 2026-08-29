import json
import os
import hashlib
from pathlib import Path
from google import genai
from google.genai import types
from pydantic import BaseModel

from services.api.config import get_settings

# Initialize the Gemini client lazily or once
_client = None

def get_gemini_client():
    global _client
    if _client is None:
        settings = get_settings()
        if settings.gemini_api_key:
            _client = genai.Client(api_key=settings.gemini_api_key)
        else:
            # For testing with fake keys or DEMO_MODE
            _client = genai.Client(api_key="fake-key-for-tests")
    return _client

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
            prompt_token_count=10,
            candidates_token_count=10,
            total_token_count=20
        )

async def generate_content_async(
    agent_name: str,
    model_id: str,
    prompt: str,
    context: dict,
    output_model: type[BaseModel]
) -> any:
    """
    Wraps the Gemini call, handles DEMO_MODE (loading fixtures),
    and RECORD_FIXTURES (saving responses).
    """
    settings = get_settings()
    
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
    client = get_gemini_client()
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=output_model,
        temperature=0.0
    )
    
    response = await client.aio.models.generate_content(
        model=model_id,
        contents=prompt,
        config=config
    )
    
    # Record fixture if needed
    if settings.record_fixtures and response.parsed:
        path = _get_fixture_path(agent_name, context)
        # Convert pydantic model to dict
        data = response.parsed.model_dump()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
    return response
