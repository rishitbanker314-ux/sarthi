import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import os
os.environ["DEV_JWT_SECRET"] = "test-secret"
os.environ["AUTH_MODE"] = "local"
os.environ["SUPABASE_JWKS_URL"] = "http://fake"
os.environ["ALEMBIC_DATABASE_URL"] = "postgresql+asyncpg://sarathi:sarathi@localhost:5432/sarathi"

from services.api.main import app
from services.api.db import get_session
from services.api.models.base import Base
from services.api.config import get_settings

settings = get_settings()

# Use a test DB URL or default for local tests
TEST_DB_URL = "postgresql+asyncpg://sarathi:sarathi@localhost:5432/sarathi"

@pytest_asyncio.fixture
async def db_session():
    """Provides a transactional database session."""
    engine = create_async_engine(TEST_DB_URL, pool_pre_ping=True)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async_session = async_sessionmaker(bind=connection, expire_on_commit=False)
        
        async with async_session() as session:
            yield session
            
        await transaction.rollback()
    await engine.dispose()

@pytest_asyncio.fixture
async def client(db_session):
    """Provides a test client with overridden dependencies."""
    app.dependency_overrides[get_session] = lambda: db_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()

@pytest.fixture
def token_headers():
    """Provides valid JWT headers for tests using the dev token generator."""
    from services.api.routers.dev_auth import dev_user_id
    import jwt
    import time
    
    email = "test@example.com"
    uid = dev_user_id(email)
    
    payload = {
        "sub": str(uid),
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    
    token = jwt.encode(payload, settings.dev_jwt_secret, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}
