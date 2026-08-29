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

@lru_cache
def get_settings() -> Settings:
    return Settings()
