from functools import lru_cache
from pydantic_settings import BaseSettings

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
    dev_jwt_secret: str = ""
    cors_origins: str = "*"
    record_fixtures: bool = False

    model_config = {"env_file": ".env"}

    from pydantic import model_validator
    
    @model_validator(mode="after")
    def validate_production_safety(self) -> 'Settings':
        if self.env == "production":
            if self.auth_mode == "local":
                raise ValueError("Cannot run with auth_mode='local' in production.")
            if self.demo_mode is True:
                raise ValueError("Cannot run with demo_mode=True in production.")
            if not self.dev_jwt_secret or self.dev_jwt_secret in ["", "supersecret"]:
                raise ValueError("dev_jwt_secret cannot be empty or default in production.")
            if "*" in self.cors_origins.split(","):
                raise ValueError("cors_origins cannot contain wildcard '*' in production.")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()
