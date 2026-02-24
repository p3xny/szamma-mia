from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "email IS NOT NULL OR phone IS NOT NULL",
            name="ck_users_email_or_phone",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    addresses: Mapped[List["UserAddress"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    orders: Mapped[List["Order"]] = relationship(back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(50), unique=True)
    label: Mapped[str] = mapped_column(String(100))
    display_order: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)

    dishes: Mapped[List["Dish"]] = relationship(back_populates="category")


class Dish(Base):
    __tablename__ = "dishes"
    __table_args__ = (
        CheckConstraint(
            "original_price IS NULL OR original_price > base_price",
            name="ck_dishes_original_gt_base",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    base_price: Mapped[Decimal] = mapped_column()
    original_price: Mapped[Optional[Decimal]] = mapped_column()
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_daily_special: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    display_order: Mapped[int] = mapped_column(default=0)

    category: Mapped["Category"] = relationship(back_populates="dishes")
    dish_ingredients: Mapped[List["DishIngredient"]] = relationship(
        back_populates="dish", cascade="all, delete-orphan"
    )
    dish_extras: Mapped[List["DishExtra"]] = relationship(
        back_populates="dish", cascade="all, delete-orphan"
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    dish_ingredients: Mapped[List["DishIngredient"]] = relationship(
        back_populates="ingredient"
    )


class DishIngredient(Base):
    __tablename__ = "dish_ingredients"
    __table_args__ = (
        UniqueConstraint("dish_id", "ingredient_id", name="uq_dish_ingredient"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dish_id: Mapped[int] = mapped_column(
        ForeignKey("dishes.id", ondelete="CASCADE")
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="RESTRICT")
    )
    is_included_by_default: Mapped[bool] = mapped_column(default=True)
    additional_price: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    display_order: Mapped[int] = mapped_column(default=0)

    dish: Mapped["Dish"] = relationship(back_populates="dish_ingredients")
    ingredient: Mapped["Ingredient"] = relationship(
        back_populates="dish_ingredients"
    )


class Extra(Base):
    __tablename__ = "extras"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    dish_extras: Mapped[List["DishExtra"]] = relationship(
        back_populates="extra"
    )


class DishExtra(Base):
    __tablename__ = "dish_extras"
    __table_args__ = (
        UniqueConstraint("dish_id", "extra_id", name="uq_dish_extra"),
        CheckConstraint("price > 0", name="ck_dish_extras_price_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dish_id: Mapped[int] = mapped_column(
        ForeignKey("dishes.id", ondelete="CASCADE")
    )
    extra_id: Mapped[int] = mapped_column(
        ForeignKey("extras.id", ondelete="RESTRICT")
    )
    price: Mapped[Decimal] = mapped_column()
    display_order: Mapped[int] = mapped_column(default=0)

    dish: Mapped["Dish"] = relationship(back_populates="dish_extras")
    extra: Mapped["Extra"] = relationship(back_populates="dish_extras")


class UserAddress(Base):
    __tablename__ = "user_addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    label: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    street: Mapped[str] = mapped_column(String(200))
    house_number: Mapped[str] = mapped_column(String(20))
    apartment: Mapped[Optional[str]] = mapped_column(String(20))
    is_default: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="addresses")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, confirmed, preparing, delivering, completed, cancelled
    delivery_mode: Mapped[str] = mapped_column(String(20))  # delivery, pickup
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    street: Mapped[Optional[str]] = mapped_column(String(200))
    house_number: Mapped[Optional[str]] = mapped_column(String(20))
    apartment: Mapped[Optional[str]] = mapped_column(String(20))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    payment_method: Mapped[str] = mapped_column(String(30))
    coupon_code: Mapped[Optional[str]] = mapped_column(String(50))
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date)
    scheduled_time: Mapped[Optional[str]] = mapped_column(String(5))
    eta_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)
    items_total: Mapped[Decimal] = mapped_column()
    delivery_fee: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    discount: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    total: Mapped[Decimal] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    discount_type: Mapped[str] = mapped_column(String(10), default="percent")  # percent, fixed
    discount_percent: Mapped[int] = mapped_column(default=0)
    discount_amount: Mapped[Optional[Decimal]] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class EventBanner(Base):
    __tablename__ = "event_banners"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    subtitle: Mapped[Optional[str]] = mapped_column(String(300))
    image_url: Mapped[str] = mapped_column(String(500))
    link_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class SiteSetting(Base):
    __tablename__ = "site_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class RestaurantTable(Base):
    __tablename__ = "restaurant_tables"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(20))
    seats: Mapped[int] = mapped_column(default=4)
    zone: Mapped[str] = mapped_column(String(20))  # indoor, outdoor
    position_x: Mapped[float] = mapped_column(default=0)
    position_y: Mapped[float] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    display_order: Mapped[int] = mapped_column(default=0)

    reservations: Mapped[List["Reservation"]] = relationship(
        back_populates="table", cascade="all, delete-orphan"
    )


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    table_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant_tables.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    reservation_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[str] = mapped_column(String(5))  # "19:00"
    guest_name: Mapped[str] = mapped_column(String(100))
    guest_phone: Mapped[str] = mapped_column(String(20))
    guests_count: Mapped[int] = mapped_column(default=2)
    status: Mapped[str] = mapped_column(
        String(20), default="confirmed"
    )  # confirmed, cancelled
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    table: Mapped["RestaurantTable"] = relationship(back_populates="reservations")
    user: Mapped["User"] = relationship()


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50))  # reservation
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class PushSubscription(Base):
    """Web Push subscription for a staff/admin device."""

    __tablename__ = "push_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    endpoint: Mapped[str] = mapped_column(Text, unique=True)
    p256dh: Mapped[str] = mapped_column(Text)
    auth: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE")
    )
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"))
    dish_name: Mapped[str] = mapped_column(String(200))
    base_price: Mapped[Decimal] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    ingredients_snapshot: Mapped[Optional[str]] = mapped_column(Text)
    extras_snapshot: Mapped[Optional[str]] = mapped_column(Text)
    item_total: Mapped[Decimal] = mapped_column()

    order: Mapped["Order"] = relationship(back_populates="items")
