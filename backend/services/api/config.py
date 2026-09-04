from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import model_validator
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    env: str = "development"
    demo_mode: bool = False
    auth_mode: str = "supabase"
    database_url: str = ""
    alembic_database_url: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwks_url: str = ""
    gemini_api_key: str = ""
    gemini_api_keys: str = "" # Comma-separated list of keys
    dev_jwt_secret: str = ""
    cors_origins: str = "*"
    record_fixtures: bool = False
    model_profile: str = "demo"
    max_concurrent_users: int = 3

    model_config = {"env_file": ".env"}

    @model_validator(mode="after")
    def validate_model_profile(self) -> 'Settings':
        if self.model_profile not in ["demo", "economy", "free"]:
            raise ValueError(f"Invalid MODEL_PROFILE: {self.model_profile}. Allowed values: 'economy', 'free', 'demo'")
        
        if self.model_profile == "economy":
            logger.warning("MODEL_PROFILE=economy - Planner is on FLASH, rationale quality reduced. Set MODEL_PROFILE=demo or free before any rehearsal or demo.")
            
        return self

    def get_agent_tier(self, agent_name: str) -> str:
        if self.model_profile == "economy":
            return "flash"
        elif self.model_profile == "free":
            # free = all flash because Pro has no free-tier quota (checked 2026-09-04)
            return "flash"
        else:
            # demo profile
            if agent_name in ["planner", "adaptor"]:
                return "pro"
            return "flash"

    def get_api_keys(self) -> list[str]:
        keys = []
        if self.gemini_api_keys:
            keys.extend([k.strip() for k in self.gemini_api_keys.split(",") if k.strip()])
        if self.gemini_api_key and self.gemini_api_key not in keys:
            keys.append(self.gemini_api_key.strip())
        return keys
    
    @model_validator(mode="after")
    def validate_production_safety(self) -> 'Settings':
        if self.env == "production":
            if self.auth_mode == "local":
                raise ValueError("Cannot run with auth_mode='local' in production.")
            if self.demo_mode is True:
                raise ValueError("Cannot run with demo_mode=True in production.")
            if "*" in self.cors_origins.split(","):
                raise ValueError("cors_origins cannot contain wildcard '*' in production.")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()
