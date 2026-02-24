from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, model_validator


# --- Categories ---


class CategoryCreate(BaseModel):
    key: str
    label: str
    display_order: int = 0
    is_active: bool = True


class CategoryUpdate(BaseModel):
    key: Optional[str] = None
    label: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    id: int
    key: str
    label: str
    display_order: int
    is_active: bool


# --- Ingredients ---


class IngredientCreate(BaseModel):
    name: str


class IngredientResponse(BaseModel):
    id: int
    name: str
    is_active: bool


# --- Extras ---


class ExtraCreate(BaseModel):
    name: str


class ExtraResponse(BaseModel):
    id: int
    name: str
    is_active: bool


# --- Dish ingredients ---


class DishIngredientCreate(BaseModel):
    ingredient_id: int
    is_included_by_default: bool = True
    additional_price: Decimal = Decimal("0")
    display_order: int = 0


class DishIngredientUpdate(BaseModel):
    is_included_by_default: Optional[bool] = None
    additional_price: Optional[Decimal] = None
    display_order: Optional[int] = None


class DishIngredientResponse(BaseModel):
    id: int
    ingredient_id: int
    ingredient_name: str
    is_included_by_default: bool
    additional_price: Decimal
    display_order: int


# --- Dish extras ---


class DishExtraCreate(BaseModel):
    extra_id: int
    price: Decimal
    display_order: int = 0


class DishExtraUpdate(BaseModel):
    price: Optional[Decimal] = None
    display_order: Optional[int] = None


class DishExtraResponse(BaseModel):
    id: int
    extra_id: int
    extra_name: str
    price: Decimal
    display_order: int


# --- Dishes ---


class DishCreate(BaseModel):
    name: str
    category_id: int
    base_price: Decimal
    original_price: Optional[Decimal] = None
    image_url: Optional[str] = None
    is_daily_special: bool = False
    is_active: bool = True
    display_order: int = 0


class DishUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    base_price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    image_url: Optional[str] = None
    is_daily_special: Optional[bool] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class DishResponse(BaseModel):
    id: int
    name: str
    category_id: int
    category_label: str
    base_price: Decimal
    original_price: Optional[Decimal] = None
    image_url: Optional[str] = None
    is_daily_special: bool
    is_active: bool
    display_order: int
    ingredients: list[DishIngredientResponse]
    extras: list[DishExtraResponse]


# --- Coupons ---


class CouponCreate(BaseModel):
    code: str
    discount_type: str = "percent"  # percent, fixed
    discount_percent: int = 0
    discount_amount: Optional[Decimal] = None
    is_active: bool = True


class CouponUpdate(BaseModel):
    code: Optional[str] = None
    discount_type: Optional[str] = None
    discount_percent: Optional[int] = None
    discount_amount: Optional[Decimal] = None
    is_active: Optional[bool] = None


class CouponResponse(BaseModel):
    id: int
    code: str
    discount_type: str
    discount_percent: int
    discount_amount: Optional[Decimal] = None
    is_active: bool


# --- Event banners ---


class EventBannerCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    image_url: str
    link_url: Optional[str] = None
    is_active: bool = False


class EventBannerUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    is_active: Optional[bool] = None


class EventBannerResponse(BaseModel):
    id: int
    title: str
    subtitle: Optional[str] = None
    image_url: str
    link_url: Optional[str] = None
    is_active: bool


# --- Site settings ---


# --- Tables ---


class TableCreate(BaseModel):
    label: str
    seats: int = 4
    zone: str  # indoor, outdoor
    position_x: float = 0
    position_y: float = 0
    is_active: bool = True
    display_order: int = 0


class TableUpdate(BaseModel):
    label: Optional[str] = None
    seats: Optional[int] = None
    zone: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class TableResponse(BaseModel):
    id: int
    label: str
    seats: int
    zone: str
    position_x: float
    position_y: float
    is_active: bool
    display_order: int


# --- Reservations ---


class ReservationResponse(BaseModel):
    id: int
    table_id: int
    table_label: str
    user_id: int
    guest_name: str
    guest_phone: str
    reservation_date: str
    start_time: str
    guests_count: int
    status: str
    notes: Optional[str] = None
    created_at: str


class ReservationUpdate(BaseModel):
    status: Optional[str] = None


# --- Notifications ---


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    is_read: bool
    created_at: str


# --- Orders ---


class AdminOrderItemResponse(BaseModel):
    id: int
    dish_id: int
    dish_name: str
    base_price: Decimal
    quantity: int
    ingredients_snapshot: Optional[str] = None
    extras_snapshot: Optional[str] = None
    item_total: Decimal


class AdminOrderResponse(BaseModel):
    id: int
    status: str
    delivery_mode: str
    first_name: str
    last_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    apartment: Optional[str] = None
    notes: Optional[str] = None
    payment_method: str
    coupon_code: Optional[str] = None
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    eta_minutes: Optional[int] = None
    items_total: Decimal
    delivery_fee: Decimal
    discount: Decimal
    total: Decimal
    created_at: str
    items: list[AdminOrderItemResponse]


class OrderStatusUpdate(BaseModel):
    status: str
    eta_minutes: Optional[int] = None


# --- Site settings ---


class SettingsUpdate(BaseModel):
    phone: Optional[str] = None
    reservation_duration: Optional[str] = None
    eta_step: Optional[str] = None
    eta_default: Optional[str] = None


class SettingsResponse(BaseModel):
    phone: str
    reservation_duration: str
    eta_step: str
    eta_default: str
