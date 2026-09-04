import pytest
from services.api.config import get_settings

def test_demo_profile_agent_tiers():
    settings = get_settings()
    original_profile = settings.model_profile
    
    try:
        # Test economy profile
        settings.model_profile = "economy"
        assert settings.get_agent_tier("diagnostician") == "flash"
        assert settings.get_agent_tier("planner") == "flash"
        assert settings.get_agent_tier("adaptor") == "flash"
        
        # Test free profile
        settings.model_profile = "free"
        assert settings.get_agent_tier("diagnostician") == "flash"
        assert settings.get_agent_tier("planner") == "pro"
        assert settings.get_agent_tier("tutor") == "flash"
        assert settings.get_agent_tier("adaptor") == "flash"

        # Test demo profile
        settings.model_profile = "demo"
        assert settings.get_agent_tier("diagnostician") == "flash"
        assert settings.get_agent_tier("planner") == "pro"
        assert settings.get_agent_tier("tutor") == "flash"
        assert settings.get_agent_tier("assessor") == "flash"
        assert settings.get_agent_tier("adaptor") == "pro"
    finally:
        settings.model_profile = original_profile
