import pytest
import os
import json
from pathlib import Path
from pydantic import BaseModel, Field
from unittest.mock import patch, AsyncMock

from services.agents.base import run
from services.agents.usage import usage_stats
from services.api.config import get_settings

class SmokeAnswer(BaseModel):
    answer: str = Field(description="The answer")
    confidence: float = Field(description="Confidence from 0 to 1")

@pytest.fixture(autouse=True)
def setup_prompts_dir():
    # Ensure the prompts directory exists for the test
    prompts_dir = Path(__file__).parent.parent / "services" / "agents" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    test_template = prompts_dir / "_test_prompt.md"
    test_template.write_text("Hello {{name}}")
    yield
    if test_template.exists():
        test_template.unlink()

@pytest.fixture
def mock_gemini():
    with patch("services.agents.client.get_gemini_client") as mock:
        client_instance = AsyncMock()
        mock.return_value = client_instance
        yield client_instance

@pytest.mark.asyncio
async def test_base_run_success(mock_gemini):
    # Setup mock response
    class FakeParsedResponse:
        def __init__(self):
            self.parsed = SmokeAnswer(answer="Success", confidence=1.0)
            self.usage_metadata = type("Usage", (), {
                "prompt_token_count": 5,
                "candidates_token_count": 10,
                "total_token_count": 15
            })()
            
    mock_gemini.aio.models.generate_content.return_value = FakeParsedResponse()

    # Clear usage stats for clean test
    usage_stats._stats.clear()

    result = await run(
        agent_name="test_agent",
        prompt_template_path="_test_prompt.md",
        context={"name": "Alice"},
        output_model=SmokeAnswer,
        model_tier="flash"
    )

    assert result.answer == "Success"
    assert result.confidence == 1.0
    
    stats = await usage_stats.get_all()
    assert stats["test_agent"]["calls"] == 1
    assert stats["test_agent"]["retries"] == 0
    assert stats["test_agent"]["fallbacks"] == 0
    assert stats["test_agent"]["input_tokens"] == 5

@pytest.mark.asyncio
async def test_base_run_invalid_then_valid(mock_gemini):
    class ValidResponse:
        def __init__(self):
            self.parsed = SmokeAnswer(answer="Success", confidence=1.0)
            self.usage_metadata = type("Usage", (), {
                "prompt_token_count": 10,
                "candidates_token_count": 10,
                "total_token_count": 20
            })()
            
    class InvalidResponse:
        def __init__(self):
            self.parsed = None # Simulating validation failure / pydantic parse fail in SDK
            
    # Mock to raise ValueError on first call (simulating parse error) and return valid on second
    mock_gemini.aio.models.generate_content.side_effect = [
        ValueError("Invalid JSON"),
        ValidResponse()
    ]

    usage_stats._stats.clear()

    result = await run(
        agent_name="test_agent_retry",
        prompt_template_path="_test_prompt.md",
        context={"name": "Bob"},
        output_model=SmokeAnswer,
        model_tier="flash"
    )

    assert result.answer == "Success"
    
    stats = await usage_stats.get_all()
    assert stats["test_agent_retry"]["calls"] == 1
    assert stats["test_agent_retry"]["retries"] == 1
    assert stats["test_agent_retry"]["fallbacks"] == 0

@pytest.mark.asyncio
async def test_base_run_invalid_twice_falls_back(mock_gemini):
    mock_gemini.aio.models.generate_content.side_effect = [
        ValueError("Invalid JSON 1"),
        ValueError("Invalid JSON 2")
    ]

    usage_stats._stats.clear()
    
    def fallback():
        return SmokeAnswer(answer="Fallback", confidence=0.0)

    result = await run(
        agent_name="test_agent_fallback",
        prompt_template_path="_test_prompt.md",
        context={"name": "Charlie"},
        output_model=SmokeAnswer,
        model_tier="flash",
        fallback_factory=fallback
    )

    assert result.answer == "Fallback"
    
    stats = await usage_stats.get_all()
    assert stats["test_agent_fallback"]["calls"] == 1
    assert stats["test_agent_fallback"]["retries"] == 1
    assert stats["test_agent_fallback"]["fallbacks"] == 1

@pytest.mark.asyncio
async def test_demo_mode_fallback():
    # Force settings.demo_mode = True for this test and fake api key
    settings = get_settings()
    settings.demo_mode = True
    settings.gemini_api_key = "invalid-key"
    
    usage_stats._stats.clear()
    
    # Run the base run with _smoke_default.json
    result = await run(
        agent_name="_smoke",
        prompt_template_path="_test_prompt.md",
        context={"name": "Demo"},
        output_model=SmokeAnswer,
        model_tier="flash"
    )
    
    assert result.answer == "Paris"
    assert result.confidence == 0.99
    
    stats = await usage_stats.get_all()
    assert stats["_smoke"]["calls"] == 1
    assert stats["_smoke"]["input_tokens"] == 10 # Hardcoded in _FakeResponse
    assert stats["_smoke"]["output_tokens"] == 10
    
    # Restore
    settings.demo_mode = False
