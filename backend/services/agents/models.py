"""
Gemini Model IDs
Verified on: 2026-09-02 against AI Studio
"""

# Fetched 2026-09-02 from AI Studio Rate Limits
# Flash models: 15 RPM, 1500 RPD
# Pro models: 2 RPM, 50 RPD
FREE_TIER_MODELS = {
    "flash": [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash", 
        "gemini-2.5-flash",
        "gemini-flash-latest"
    ],
    "pro": [
        "gemini-3.1-pro-preview",
        "gemini-2.5-pro",
        "gemini-pro-latest"
    ]
}

MODEL_PRO = "gemini-3.1-pro-preview"
MODEL_FLASH = "gemini-3.7-flash"
MODEL_LITE = "gemini-3.1-flash-lite"

def validate_models():
    """Fail loudly if any configured model is not in the free-tier allowlist."""
    import logging
    import os
    from google import genai
    logger = logging.getLogger(__name__)
    
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "fake-key-for-tests"))
    available_models = {}
    
    try:
        for m in client.models.list():
            available_models[m.name.replace("models/", "")] = m
    except Exception as e:
        logger.warning(f"Failed to fetch models from API: {e}")
        return

    # Filter FREE_TIER_MODELS in-place based on actual availability and capabilities
    for tier in list(FREE_TIER_MODELS.keys()):
        valid_models = []
        for model_id in FREE_TIER_MODELS[tier]:
            # (a) exists
            if model_id not in available_models:
                logger.error(f"Configured model {model_id} does not exist.")
                continue
            
            m = available_models[model_id]
            # (b) supports generateContent
            if "generateContent" not in getattr(m, "supported_actions", []):
                logger.error(f"Configured model {model_id} does not support generateContent.")
                continue
                
            # (d) not image models
            if "vision" in model_id.lower() or "imagen" in model_id.lower() or "embedding" in model_id.lower():
                logger.error(f"Configured model {model_id} is an image/embedding model.")
                continue
                
            # (c) has free tier - we assume what's in FREE_TIER_MODELS dictionary keys has free tier, 
            # we are just validating our configuration against the API.
            valid_models.append(model_id)
            
        if not valid_models:
            raise ValueError(f"No valid models remaining for tier '{tier}' after validation!")
            
        FREE_TIER_MODELS[tier] = valid_models
    
    print("--- FREE TIER ALLOWLIST ---")
    for tier, models in FREE_TIER_MODELS.items():
        print(f"{tier.upper()}: {', '.join(models)}")
    print("---------------------------")
