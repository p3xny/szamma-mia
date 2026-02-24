import os

os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

import pytest
from decimal import Decimal
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models import (
    Base, Category, Coupon, Dish, DishExtra, DishIngredient,
    Extra, Ingredient, User,
)
from auth import hash_password, create_access_token
from database import get_db
from main import app


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(db_engine):
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False,
    )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def seed_menu(db_session):
    """Seed a category + dish costing 30 zł so two items meet the 50 zł minimum."""
    cat = Category(key="pizza", label="Pizza", display_order=0)
    db_session.add(cat)
    await db_session.flush()

    ing = Ingredient(name="Ser")
    ext = Extra(name="Jalapeño")
    db_session.add_all([ing, ext])
    await db_session.flush()

    dish = Dish(
        name="Margherita",
        category_id=cat.id,
        base_price=Decimal("30"),
        display_order=0,
    )
    db_session.add(dish)
    await db_session.flush()

    di = DishIngredient(
        dish_id=dish.id, ingredient_id=ing.id,
        is_included_by_default=True, additional_price=Decimal("0"),
    )
    de = DishExtra(
        dish_id=dish.id, extra_id=ext.id, price=Decimal("5"),
    )
    coupon = Coupon(code="SZAMMA10", discount_percent=10, is_active=True)
    db_session.add_all([di, de, coupon])
    await db_session.commit()
    return dish


@pytest.fixture
async def registered_user(db_session):
    """Create a user with known credentials and return (user, token)."""
    user = User(
        email="user@test.pl",
        first_name="Jan",
        phone="123456789",
        password_hash=hash_password("haslo123"),
        role="user",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token(user.id)
    return user, token


@pytest.fixture
async def admin_user(db_session):
    """Create an admin user and return (user, token)."""
    user = User(
        email="admin@test.pl",
        first_name="Admin",
        phone="000000000",
        password_hash=hash_password("admin123"),
        role="admin",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token(user.id)
    return user, token


@pytest.fixture
async def seed_coupon(db_session):
    """Seed the SZAMMA10 coupon for coupon-related tests."""
    coupon = Coupon(code="SZAMMA10", discount_percent=10, is_active=True)
    db_session.add(coupon)
    await db_session.commit()
    return coupon


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
