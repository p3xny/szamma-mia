from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr


# --- Auth ---


class RegisterRequest(BaseModel):
    email: EmailStr
    first_name: str
    phone: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    role: str


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class AddressCreate(BaseModel):
    label: Optional[str] = None
    city: str
    street: str
    house_number: str
    apartment: Optional[str] = None
    is_default: bool = False


class AddressUpdate(BaseModel):
    label: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    apartment: Optional[str] = None
    is_default: Optional[bool] = None


class AddressResponse(BaseModel):
    id: int
    label: Optional[str] = None
    city: str
    street: str
    house_number: str
    apartment: Optional[str] = None
    is_default: bool


# --- Order creation ---


class IngredientSnapshot(BaseModel):
    name: str
    included: bool
    price: Decimal = Decimal("0")


class ExtraSnapshot(BaseModel):
    name: str
    price: Decimal


class OrderItemCreate(BaseModel):
    dish_id: int
    quantity: int
    ingredients: list[IngredientSnapshot] = []
    extras: list[ExtraSnapshot] = []


class OrderCreate(BaseModel):
    delivery_mode: str  # delivery | pickup
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
    items: list[OrderItemCreate]


# --- Order response ---


class OrderItemResponse(BaseModel):
    id: int
    dish_id: int
    dish_name: str
    base_price: Decimal
    quantity: int
    ingredients_snapshot: Optional[str] = None
    extras_snapshot: Optional[str] = None
    item_total: Decimal


class OrderResponse(BaseModel):
    id: int
    status: str
    delivery_mode: str
    first_name: str
    last_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    payment_method: str
    coupon_code: Optional[str] = None
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    eta_minutes: Optional[int] = None
    items_total: Decimal
    delivery_fee: Decimal
    discount: Decimal
    total: Decimal
    items: list[OrderItemResponse]


# --- Coupon ---


class CouponValidateRequest(BaseModel):
    code: str


class CouponValidateResponse(BaseModel):
    valid: bool
    discount_type: str = "percent"  # percent, fixed
    discount_percent: int = 0
    discount_amount: float = 0
    message: str
