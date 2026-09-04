import asyncio
from typing import Dict, Any

class UsageStats:
    def __init__(self):
        self._stats: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def record(
        self,
        agent_name: str,
        model_tier: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        retried: bool,
        fell_back: bool
    ):
        async with self._lock:
            if agent_name not in self._stats:
                self._stats[agent_name] = {
                    "calls": 0,
                    "model_tier": model_tier,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "latency_ms": 0,
                    "retries": 0,
                    "fallbacks": 0,
                }
            
            s = self._stats[agent_name]
            s["calls"] += 1
            s["model_tier"] = model_tier # Update in case it changes
            s["input_tokens"] += input_tokens
            s["output_tokens"] += output_tokens
            s["latency_ms"] += latency_ms
            if retried:
                s["retries"] += 1
            if fell_back:
                s["fallbacks"] += 1
            
            # Source: https://ai.google.dev/gemini-api/docs/pricing (as of Sept 3, 2026)
            # Flash: $0.75 in / $3.75 out per 1M
            # Pro: $2.00 in / $12.00 out per 1M
            USD_TO_INR = 84.0
            
            if "pro" in model_tier.lower():
                input_cost_1m_usd = 2.00
                output_cost_1m_usd = 12.00
            else:
                input_cost_1m_usd = 0.75
                output_cost_1m_usd = 3.75
                
            cost_usd = (input_tokens / 1_000_000 * input_cost_1m_usd) + (output_tokens / 1_000_000 * output_cost_1m_usd)
            cost_inr = cost_usd * USD_TO_INR
            s["total_cost_inr"] = s.get("total_cost_inr", 0.0) + cost_inr

    async def get_all(self) -> Dict[str, Dict[str, Any]]:
        async with self._lock:
            # Return a copy to avoid mutation during iteration elsewhere
            return {k: v.copy() for k, v in self._stats.items()}

# Global accumulator
usage_stats = UsageStats()
