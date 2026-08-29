import asyncio
import time
import logging
from pathlib import Path
from typing import Callable, Any
from pydantic import BaseModel, ValidationError

from services.agents.client import generate_content_async
from services.agents.usage import usage_stats

logger = logging.getLogger(__name__)

async def run(
    agent_name: str,
    prompt_template_path: str,
    context: dict,
    output_model: type[BaseModel],
    model_tier: str,
    fallback_factory: Callable[[], Any] | None = None
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

    # 2. Setup timeouts and model id
    if model_tier.lower() == "flash":
        timeout = 20.0
        model_id = "gemini-3.7-flash" # Default flash, can pull from models.py
    else:
        timeout = 110.0
        model_id = "gemini-3.1-pro-preview"
    
    attempts = 0
    max_attempts = 2
    current_prompt = prompt
    
    total_input_tokens = 0
    total_output_tokens = 0
    start_time = time.time()
    retried = False
    fell_back = False

    while attempts < max_attempts:
        attempts += 1
        try:
            response = await asyncio.wait_for(
                generate_content_async(
                    agent_name=agent_name,
                    model_id=model_id,
                    prompt=current_prompt,
                    context=context,
                    output_model=output_model
                ),
                timeout=timeout
            )
            
            # Record usage
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                total_input_tokens += getattr(response.usage_metadata, "prompt_token_count", 0)
                total_output_tokens += getattr(response.usage_metadata, "candidates_token_count", 0)

            # 4. Return parsed response if valid
            if response.parsed:
                # pydantic validates during SDK parsing, but we double check or just return
                latency_ms = int((time.time() - start_time) * 1000)
                await usage_stats.record(agent_name, total_input_tokens, total_output_tokens, latency_ms, retried, fell_back)
                return response.parsed
                
            raise ValueError("No parsed response returned")

        except Exception as e:
            # Handle validation error or other failures
            # If it's a validation error from our end or SDK end, we can retry
            if attempts < max_attempts:
                retried = True
                error_msg = str(e)
                current_prompt = f"{prompt}\n\nValidation failed with error:\n{error_msg}\n\nPlease fix the JSON and try again."
                continue
            else:
                break
    
    # 6. Fallback
    fell_back = True
    latency_ms = int((time.time() - start_time) * 1000)
    await usage_stats.record(agent_name, total_input_tokens, total_output_tokens, latency_ms, retried, fell_back)
    
    logger.error("Agent %s fell back after %d attempts", agent_name, attempts)
    
    if fallback_factory:
        return fallback_factory()
    return None
