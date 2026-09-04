import asyncio
import time
import json

import structlog
from pathlib import Path
from typing import Callable, Any
from pydantic import BaseModel, ValidationError

from services.agents.client import generate_content_async
from services.agents.usage import usage_stats
from services.agents.models import FREE_TIER_MODELS
from services.api.config import get_settings

logger = structlog.get_logger()

async def run(
    agent_name: str,
    prompt_template_path: str,
    context: dict,
    output_model: type[BaseModel],
    model_tier: str,
    fallback_factory: Callable[[], Any] | None = None,
    strict_model: type[BaseModel] | None = None,
    validation_context: dict | None = None,
    use_schema: bool = True,
    pacing_timeout: float | None = None,
    progress_callback: Callable[[str], Any] | None = None
) -> Any:
    """
    Executes an agent with the given context and template.
    Returns the parsed output_model.
    """
    # 1. Load and render template
    template_path = Path(__file__).parent / "prompts" / prompt_template_path
    if not template_path.exists():
        # Maybe absolute or relative to project root? We assume relative to services/agents/prompts
        pass
    
    with open(template_path, "r", encoding="utf-8") as f:
        prompt = f.read()
    
    # Simple replacement for context
    # E.g. replace {{key}} with value
    for k, v in context.items():
        prompt = prompt.replace(f"{{{{{k}}}}}", str(v))
        prompt = prompt.replace(f"{{{k}}}", str(v))

    if not use_schema:
        
        schema_json = json.dumps(output_model.model_json_schema(), indent=2)
        prompt += f"\n\nYou MUST return a single, valid JSON object matching this schema:\n```json\n{schema_json}\n```\nDo not include any other text."

    if model_tier.lower() == "flash":
        timeout = 60.0
        fallback_models = FREE_TIER_MODELS.get("flash", [])
    else:
        timeout = 110.0
        fallback_models = FREE_TIER_MODELS.get("pro", [])
        
    settings = get_settings()
    api_keys = settings.get_api_keys()
    if not api_keys:
        api_keys = [None]
    
    key_index = 0
    model_index = 0
    
    if not fallback_models:
        logger.error(f"No fallback models defined for tier {model_tier}")
        if fallback_factory:
            return fallback_factory()
        return None
        
    model_id = fallback_models[model_index]
    api_key = api_keys[key_index]
    
    attempts = 0
    max_attempts = 2
    current_prompt = prompt
    
    total_input_tokens = 0
    total_output_tokens = 0
    start_time = time.time()
    retried = False
    fell_back = False
    
    validation_retries = 0
    MAX_VALIDATION_RETRIES = 1
    api_retries = 0
    MAX_API_RETRIES = 1

    while True:
        try:
            attempts += 1
            logger.info("gemini_call_attempt", agent=agent_name, model=model_id, attempt=attempts, is_retry=retried)
            response = await asyncio.wait_for(
                generate_content_async(
                    agent_name=agent_name,
                    model_id=model_id,
                    prompt=current_prompt,
                    context=context,
                    output_model=output_model,
                    use_schema=use_schema,
                    api_key=api_key,
                    pacing_timeout=pacing_timeout,
                    progress_callback=progress_callback
                ),
                timeout=120.0
            )
            
            # Record usage
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                total_input_tokens += getattr(response.usage_metadata, "prompt_token_count", 0)
                total_output_tokens += getattr(response.usage_metadata, "candidates_token_count", 0)

            # 4. Return parsed response if valid
            if response.parsed:
                if strict_model:
                    try:
                        data = response.parsed.model_dump()
                        response.parsed = strict_model.model_validate(data, context=validation_context)
                    except ValidationError as e:
                        raise ValueError(f"Strict validation failed:\n{e}")

                # pydantic validates during SDK parsing, but we double check or just return
                latency_ms = int((time.time() - start_time) * 1000)
                await usage_stats.record(agent_name, model_tier, total_input_tokens, total_output_tokens, latency_ms, retried, fell_back)
                
                settings = get_settings()
                if settings.record_fixtures:
                    
                    import hashlib
                    # Use a hash of prompt + context keys to somewhat identify the fixture
                    fixture_name = f"{agent_name}_default.json"
                    fixture_dir = Path(__file__).parent.parent.parent / "fixtures" / "demo"
                    fixture_dir.mkdir(parents=True, exist_ok=True)
                    fixture_path = fixture_dir / fixture_name
                    with open(fixture_path, "w") as f:
                        json.dump(response.parsed.model_dump(mode="json"), f, indent=2)
                    logger.info(f"Recorded fixture to {fixture_path}")
                    
                logger.info(
                    "agent_success",
                    agent=agent_name,
                    latency_ms=latency_ms,
                    tokens_in=total_input_tokens,
                    tokens_out=total_output_tokens
                )
                    
                return response.parsed
                
            raise ValueError("No parsed response returned")

        except Exception as e:
            from google.genai.errors import APIError
            if isinstance(e, APIError):
                if e.code == 429 or e.code == 503:
                    if api_retries >= MAX_API_RETRIES:
                        logger.warning(f"Rate limited ({e.code}) and max retries exceeded. Triggering seamless fallback...", agent=agent_name)
                        break
                        
                    api_retries += 1
                    retried = True
                    
                    import re
                    delay = 15.0
                    m = re.search(r"Please retry in ([\d\.]+)s", str(e))
                    if m:
                        delay = float(m.group(1)) + 1.0
                        
                    if delay > 45.0:
                        logger.warning(f"Rate limit retry delay {delay}s too long. Triggering seamless fallback...", agent=agent_name)
                        break
                        
                    logger.warning(f"Rate limited ({e.code}) on {model_id}. Sleeping for {delay:.1f}s before retry...", agent=agent_name)
                    if progress_callback:
                        await progress_callback(f"Rate limit hit. Waiting {int(delay)}s...")
                    await asyncio.sleep(delay)
                    continue
                elif e.code == 404 or e.status == "PERMISSION_DENIED":
                    old_model = fallback_models[model_index]
                    logger.warning(f"Model {old_model} is missing or permission denied. Dropping from rotation.", agent=agent_name)
                    fallback_models.pop(model_index)
                    if not fallback_models:
                        logger.error(f"No models left in rotation for tier {model_tier}")
                        break
                    # Keep same model_index as we just popped the element, unless it was the last one
                    if model_index >= len(fallback_models):
                        model_index = 0
                    model_id = fallback_models[model_index]
                    
                    if api_retries >= MAX_API_RETRIES:
                        break
                        
                    api_retries += 1
                    retried = True
                    continue
                elif e.code == 400:
                    logger.error("agent_failed_invalid_argument", agent=agent_name, error=str(e), exc_info=True)
                    break
                else:
                    logger.error("agent_api_error", agent=agent_name, error=str(e), exc_info=True)
                    raise
            elif isinstance(e, ValueError):
                error_msg = str(e)
                if validation_retries < MAX_VALIDATION_RETRIES:
                    current_prompt = f"{prompt}\n\nValidation failed with error:\n{error_msg}\n\nPlease fix the JSON and try again."
                    retried = True
                    validation_retries += 1
                    logger.warning("agent_validation_retry", agent=agent_name, attempt=attempts, error=error_msg)
                    continue
                else:
                    logger.error("agent_failed", agent=agent_name, error=error_msg, exc_info=True)
                    break
            elif "Capacity wait exceeded timeout" in str(e):
                logger.warning("agent_capacity_timeout", agent=agent_name, timeout=pacing_timeout)
                break
            else:
                logger.error("agent_failed_unknown", agent=agent_name, error=str(e), exc_info=True)
                break
    
    # 6. Fallback
    fell_back = True
    latency_ms = int((time.time() - start_time) * 1000)
    await usage_stats.record(agent_name, model_tier, total_input_tokens, total_output_tokens, latency_ms, retried, fell_back)
    
    logger.warning("agent_fallback", agent=agent_name, attempts=attempts, latency_ms=latency_ms)
    
    if fallback_factory:
        return fallback_factory()
    return None
