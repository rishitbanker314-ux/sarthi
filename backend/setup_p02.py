import os

files = {
    "pyproject.toml": """[project]
name = "sarathi"
version = "0.1.0"
description = "Sarathi backend"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "sqlalchemy[asyncio]",
    "asyncpg",
    "psycopg[binary]",
    "alembic",
    "pydantic",
    "pydantic-settings",
    "PyJWT[crypto]",
    "httpx",
    "structlog",
    "google-genai",
]

[dependency-groups]
dev = [
    "pytest",
    "pytest-asyncio",
    "ruff",
    "black",
]

[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "function"
""",
    ".env.example": """ENV=
DEMO_MODE=
AUTH_MODE=
DATABASE_URL=
ALEMBIC_DATABASE_URL=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWKS_URL=
GEMINI_API_KEY=
DEV_JWT_SECRET=
CORS_ORIGINS=
RECORD_FIXTURES=
""",
    ".gitignore": """.env
.agents/mcp_config.json
__pycache__/
.venv/
.pytest_cache/
""",
    ".agents/mcp_config.example.json": """{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp"
      ],
      "env": {
        "SUPABASE_PROJECT_REF": "YOUR_PROJECT_REF",
        "SUPABASE_PERSONAL_ACCESS_TOKEN": "YOUR_SUPABASE_PERSONAL_ACCESS_TOKEN"
      }
    }
  }
}
""",
    "services/api/__init__.py": "",
    "services/api/config.py": """from functools import lru_cache
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
""",
    "services/api/db.py": """from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from services.api.config import get_settings

settings = get_settings()

# Use a default fallback url if none provided to avoid engine creation errors during tests
db_url = settings.database_url or "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

engine = create_async_engine(db_url, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
""",
    "services/api/routers/__init__.py": "",
    "services/api/routers/health.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from services.api.db import get_session
from services.api.config import get_settings
import importlib.metadata

router = APIRouter()
settings = get_settings()

@router.get("/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
        
    try:
        version = importlib.metadata.version("sarathi")
    except importlib.metadata.PackageNotFoundError:
        version = "0.1.0"

    return {
        "status": "ok",
        "db": db_status,
        "version": version,
        "env": settings.env
    }
""",
    "services/api/main.py": """from fastapi import FastAPI
from services.api.routers import health

app = FastAPI(title="Sarathi API", version="0.1.0")

app.include_router(health.router)
""",
    "tests/__init__.py": "",
    "tests/test_health.py": """import pytest
from httpx import AsyncClient, ASGITransport
from services.api.main import app
from unittest.mock import patch

@pytest.mark.asyncio
async def test_health():
    # We use mock to simulate the db session so it doesn't try to connect to a non-existent database during isolated tests
    with patch("services.api.routers.health.AsyncSession.execute") as mock_execute:
        # DB will be mocked to return ok for testing the endpoint logic itself
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["db"] == "ok"
            assert "version" in data
            assert "env" in data
"""
}

for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)

print("Files created successfully.")
