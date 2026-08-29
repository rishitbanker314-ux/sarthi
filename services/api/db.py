from typing import AsyncGenerator
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
