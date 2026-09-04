from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from services.agents.usage import usage_stats

router = APIRouter(prefix="/health", tags=["Health"])

RATES = {
    "flash": {"input_1m": 0.075, "output_1m": 0.30},
    "pro": {"input_1m": 1.25, "output_1m": 5.00}
}
USD_TO_INR = 83.50

class UsageResponse(BaseModel):
    agents: Dict[str, Dict[str, Any]]
    total_cost_usd: float
    total_cost_inr: float

@router.get("/usage", response_model=UsageResponse)
async def get_usage():
    stats = await usage_stats.get_all()
    
    total_cost_usd = 0.0
    for agent_name, s in stats.items():
        tier = s.get("model_tier", "flash").lower()
        if tier not in RATES:
            tier = "flash"
            
        rate = RATES[tier]
        cost_input = (s["input_tokens"] / 1_000_000) * rate["input_1m"]
        cost_output = (s["output_tokens"] / 1_000_000) * rate["output_1m"]
        
        agent_cost = cost_input + cost_output
        s["estimated_cost_usd"] = round(agent_cost, 6)
        total_cost_usd += agent_cost
        
    return UsageResponse(
        agents=stats,
        total_cost_usd=round(total_cost_usd, 6),
        total_cost_inr=round(total_cost_usd * USD_TO_INR, 2)
    )
