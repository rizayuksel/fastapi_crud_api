import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import get_password_hash

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_db():
    # Create a fresh in-memory database for each test
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    async def override_get_db():
        try:
            yield test_db
            await test_db.commit()
        except Exception:
            await test_db.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(test_db):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("Test1234"),
        first_name="Test",
        last_name="User",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def auth_token(client, test_user):
    response = await client.post(
        "/api/users/login", json={"email": test_user.email, "password": "Test1234"}
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture(scope="function")
async def test_item(test_db):
    from app.models import Item

    item = Item(
        name="Test iPhone",
        description="Test Description",
        category="electronics",
        status="active",
        is_deleted=False,
    )
    test_db.add(item)
    await test_db.commit()
    await test_db.refresh(item)
    return item
