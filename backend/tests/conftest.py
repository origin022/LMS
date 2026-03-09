import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from main import app
from src.core.dep import get_session
from src.core.config import config
import os

# استخدام رابط قاعدة البيانات من المتغيرات البيئية أو المتغير الافتراضي
database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:12345@localhost:5433/lms")
# استبدال postgresql:// بـ postgresql+asyncpg:// إذا لزم الأمر في التست
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(database_url)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def client():
    async with async_session_maker() as session:
        app.dependency_overrides[get_session] = lambda: session 
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
            
        app.dependency_overrides.clear()