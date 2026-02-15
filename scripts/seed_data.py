"""
Seed database with sample data.

Similar to Django fixtures (`python manage.py loaddata`),
this script provides initial test data for FastAPI,
where fixtures are not available out of the box.

Run: docker compose exec api python scripts/seed_data.py
"""

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models import Item, User
from app.security import get_password_hash


async def seed_database():
    """Add sample users and items"""
    print("🌱 Seeding database...")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if data already exists
        from sqlalchemy import func, select

        result = await session.execute(select(func.count(User.id)))
        user_count = result.scalar()

        if user_count > 0:
            print("⚠️  Database already has data. Skipping seed.")
            return

        # Create sample users
        users = [
            User(
                email="admin@example.com",
                hashed_password=get_password_hash("Admin1234"),
                first_name="Admin",
                last_name="User",
            ),
            User(
                email="john@example.com",
                hashed_password=get_password_hash("John1234"),
                first_name="John",
                last_name="Doe",
            ),
        ]

        for user in users:
            session.add(user)

        await session.flush()
        print(f"✅ Created {len(users)} users")

        # Create sample items
        items = [
            Item(
                name="iPhone 14",
                description="Apple smartphone",
                category="electronics",
                status="active",
            ),
            Item(
                name="MacBook Pro",
                description="Apple laptop",
                category="electronics",
                status="active",
            ),
            Item(
                name="AirPods Pro",
                description="Wireless earbuds",
                category="electronics",
                status="active",
            ),
            Item(
                name="Nike Air Max",
                description="Running shoes",
                category="clothing",
                status="active",
            ),
            Item(
                name="Levi's Jeans",
                description="Classic denim",
                category="clothing",
                status="active",
            ),
            Item(
                name="Harry Potter Book",
                description="Fantasy novel",
                category="books",
                status="active",
            ),
            Item(
                name="The Hobbit", description="Adventure novel", category="books", status="active"
            ),
            Item(
                name="Gaming Chair",
                description="Ergonomic chair",
                category="furniture",
                status="active",
            ),
            Item(
                name="Standing Desk",
                description="Adjustable desk",
                category="furniture",
                status="active",
            ),
            Item(
                name="Coffee Maker",
                description="Automatic brewer",
                category="kitchen",
                status="active",
            ),
        ]

        for item in items:
            session.add(item)

        await session.commit()
        print(f"✅ Created {len(items)} items")

    await engine.dispose()
    print("🎉 Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_database())
