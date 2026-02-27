import json
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from decimal import Decimal

from base64 import b64decode

from fastapi import BackgroundTasks, FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from autopay import (
    AUTOPAY_GATEWAY_URL,
    ONLINE_PAYMENT_METHODS,
    build_confirmation_xml,
    build_payment_params,
    parse_itn,
    verify_itn_hash,
    verify_return_hash,
)
from auth import (
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    require_user,
    verify_password,
)
from push import VAPID_PUBLIC_KEY, push_to_all_bg
from database import engine, get_db
from admin import router as admin_router
from models import (
    Category, Coupon, Dish, DishExtra, DishIngredient, EventBanner, Notification,
    Order, OrderItem, PushSubscription, Reservation, RestaurantTable, SiteSetting, User, UserAddress,
)
from schemas import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
    CouponValidateRequest,
    CouponValidateResponse,
    LoginRequest,
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UserUpdateRequest,
)

MIN_ORDER = Decimal("50")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)


# --- Auth endpoints ---


@app.post("/api/auth/register", status_code=201, response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email jest już zarejestrowany")

    user = User(
        email=data.email,
        first_name=data.first_name,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role="user",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(access_token=create_access_token(user.id))


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Nieprawidłowy email lub hasło")

    return TokenResponse(access_token=create_access_token(user.id))


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(user: User = Depends(require_user)):
    return UserResponse(
        id=user.id,
        email=user.email,
        phone=user.phone,
        first_name=user.first_name,
        role=user.role,
    )


@app.patch("/api/auth/me", response_model=UserResponse)
async def update_me(
    data: UserUpdateRequest,
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    if data.first_name is not None:
        user.first_name = data.first_name
    if data.phone is not None:
        user.phone = data.phone
    if data.email is not None and data.email != user.email:
        existing = await db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Ten email jest już zajęty")
        user.email = data.email

    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        phone=user.phone,
        first_name=user.first_name,
        role=user.role,
    )


# --- Address endpoints ---


@app.get("/api/auth/addresses", response_model=list[AddressResponse])
async def list_addresses(
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserAddress).where(UserAddress.user_id == user.id).order_by(UserAddress.created_at)
    )
    return [
        AddressResponse(
            id=a.id, label=a.label, city=a.city, street=a.street,
            house_number=a.house_number, apartment=a.apartment, is_default=a.is_default,
        )
        for a in result.scalars().all()
    ]


@app.post("/api/auth/addresses", status_code=201, response_model=AddressResponse)
async def create_address(
    data: AddressCreate,
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    addr = UserAddress(
        user_id=user.id,
        label=data.label,
        city=data.city,
        street=data.street,
        house_number=data.house_number,
        apartment=data.apartment,
        is_default=data.is_default,
    )
    db.add(addr)
    await db.commit()
    await db.refresh(addr)

    return AddressResponse(
        id=addr.id, label=addr.label, city=addr.city, street=addr.street,
        house_number=addr.house_number, apartment=addr.apartment, is_default=addr.is_default,
    )


@app.patch("/api/auth/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    data: AddressUpdate,
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserAddress).where(UserAddress.id == address_id, UserAddress.user_id == user.id)
    )
    addr = result.scalar_one_or_none()
    if not addr:
        raise HTTPException(status_code=404, detail="Adres nie znaleziony")

    if data.label is not None:
        addr.label = data.label
    if data.city is not None:
        addr.city = data.city
    if data.street is not None:
        addr.street = data.street
    if data.house_number is not None:
        addr.house_number = data.house_number
    if data.apartment is not None:
        addr.apartment = data.apartment
    if data.is_default is not None:
        addr.is_default = data.is_default

    await db.commit()
    await db.refresh(addr)

    return AddressResponse(
        id=addr.id, label=addr.label, city=addr.city, street=addr.street,
        house_number=addr.house_number, apartment=addr.apartment, is_default=addr.is_default,
    )


@app.delete("/api/auth/addresses/{address_id}", status_code=204)
async def delete_address(
    address_id: int,
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserAddress).where(UserAddress.id == address_id, UserAddress.user_id == user.id)
    )
    addr = result.scalar_one_or_none()
    if not addr:
        raise HTTPException(status_code=404, detail="Adres nie znaleziony")

    await db.delete(addr)
    await db.commit()


# --- Menu endpoints ---


@app.get("/api/menu")
async def get_menu(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Dish)
        .where(Dish.is_active.is_(True))
        .options(
            selectinload(Dish.category),
            selectinload(Dish.dish_ingredients).selectinload(
                DishIngredient.ingredient
            ),
            selectinload(Dish.dish_extras).selectinload(
                DishExtra.extra
            ),
        )
        .order_by(Dish.category_id, Dish.display_order)
    )
    dishes = result.scalars().all()

    return [
        {
            "id": d.id,
            "name": d.name,
            "category": d.category.key,
            "price": float(d.base_price),
            "originalPrice": float(d.original_price) if d.original_price else None,
            "image": d.image_url,
            "dailySpecial": d.is_daily_special,
            "ingredients": [
                {
                    "name": di.ingredient.name,
                    "included": di.is_included_by_default,
                    **({"price": float(di.additional_price)} if di.additional_price else {}),
                }
                for di in sorted(d.dish_ingredients, key=lambda x: x.display_order)
            ],
            "extras": [
                {
                    "name": de.extra.name,
                    "price": float(de.price),
                }
                for de in sorted(d.dish_extras, key=lambda x: x.display_order)
            ],
        }
        for d in dishes
    ]


@app.get("/api/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Category)
        .where(Category.is_active.is_(True))
        .order_by(Category.display_order)
    )
    return [
        {"key": c.key, "label": c.label}
        for c in result.scalars().all()
    ]


@app.post("/api/orders", status_code=201, response_model=OrderResponse)
async def create_order(
    data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not data.items:
        raise HTTPException(status_code=400, detail="Zamówienie musi zawierać przynajmniej jedną pozycję")

    if data.delivery_mode == "delivery":
        if not data.city or not data.street or not data.house_number:
            raise HTTPException(status_code=400, detail="Adres dostawy jest wymagany")

    # Fetch all referenced dishes
    dish_ids = [item.dish_id for item in data.items]
    result = await db.execute(
        select(Dish)
        .where(Dish.id.in_(dish_ids), Dish.is_active.is_(True))
        .options(
            selectinload(Dish.dish_ingredients).selectinload(DishIngredient.ingredient),
            selectinload(Dish.dish_extras).selectinload(DishExtra.extra),
        )
    )
    dishes_by_id = {d.id: d for d in result.scalars().all()}

    # Verify all dishes exist and are active
    for item in data.items:
        if item.dish_id not in dishes_by_id:
            raise HTTPException(
                status_code=400,
                detail=f"Danie o ID {item.dish_id} nie istnieje lub jest nieaktywne",
            )

    # Server-side price calculation
    items_total = Decimal("0")
    order_items = []

    for item_data in data.items:
        dish = dishes_by_id[item_data.dish_id]
        unit_price = dish.base_price

        # Add price for included (toggled-on) ingredients that have additional_price
        for ing_snap in item_data.ingredients:
            if ing_snap.included and ing_snap.price > 0:
                # Verify this ingredient exists on the dish
                for di in dish.dish_ingredients:
                    if di.ingredient.name == ing_snap.name and di.additional_price:
                        unit_price += di.additional_price
                        break

        # Add price for selected extras
        for ext_snap in item_data.extras:
            for de in dish.dish_extras:
                if de.extra.name == ext_snap.name:
                    unit_price += de.price
                    break

        line_total = unit_price * item_data.quantity
        items_total += line_total

        order_items.append(
            OrderItem(
                dish_id=dish.id,
                dish_name=dish.name,
                base_price=dish.base_price,
                quantity=item_data.quantity,
                ingredients_snapshot=json.dumps(
                    [ing.model_dump(mode="json") for ing in item_data.ingredients]
                ) if item_data.ingredients else None,
                extras_snapshot=json.dumps(
                    [ext.model_dump(mode="json") for ext in item_data.extras]
                ) if item_data.extras else None,
                item_total=line_total,
            )
        )

    if items_total < MIN_ORDER:
        raise HTTPException(
            status_code=400,
            detail=f"Minimalna wartość zamówienia to {MIN_ORDER} zł",
        )

    # Coupon discount
    discount = Decimal("0")
    if data.coupon_code:
        coupon_result = await db.execute(
            select(Coupon).where(
                Coupon.code == data.coupon_code.upper(), Coupon.is_active.is_(True)
            )
        )
        coupon = coupon_result.scalar_one_or_none()
        if coupon:
            if coupon.discount_type == "fixed" and coupon.discount_amount:
                discount = min(coupon.discount_amount, items_total)
            else:
                discount = (items_total * Decimal(str(coupon.discount_percent)) / Decimal("100")).quantize(Decimal("1"))

    total = items_total - discount

    scheduled_date = None
    if data.scheduled_date:
        try:
            scheduled_date = date.fromisoformat(data.scheduled_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Nieprawidłowy format daty")

    order = Order(
        user_id=user.id if user else None,
        status="pending",
        delivery_mode=data.delivery_mode,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        email=data.email,
        city=data.city,
        street=data.street,
        house_number=data.house_number,
        apartment=data.apartment,
        notes=data.notes,
        payment_method=data.payment_method,
        coupon_code=data.coupon_code,
        scheduled_date=scheduled_date,
        scheduled_time=data.scheduled_time,
        items_total=items_total,
        delivery_fee=Decimal("0"),
        discount=discount,
        total=total,
        items=order_items,
    )

    db.add(order)
    await db.commit()
    await db.refresh(order, attribute_names=["items"])

    # TODO: For remote payment methods (blik, card-online, transfer), this notification
    # should be created only after successful payment confirmation, not at order creation time.
    # For local payment methods (cash, card-delivery), immediate notification is correct.
    notification = Notification(
        type="order",
        title=f"Nowe zamówienie #{order.id}",
        message=f"{order.first_name} — {order.delivery_mode}, {order.total} zł, płatność: {order.payment_method}",
    )
    db.add(notification)
    await db.commit()

    background_tasks.add_task(push_to_all_bg, {
        "type": "order",
        "id": order.id,
        "title": f"🍕 Nowe zamówienie #{order.id}",
        "body": f"{order.first_name} — {order.delivery_mode}, {float(order.total):.2f} zł",
        "url": "/",
    })

    return _order_to_response(order)


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Zamówienie nie znalezione")
    return _order_to_response(order)


@app.get("/api/my-orders", response_model=list[OrderResponse])
async def get_my_orders(
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    active_statuses = ("pending", "confirmed", "preparing", "delivering")
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user.id, Order.status.in_(active_statuses))
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    return [_order_to_response(o) for o in result.scalars().all()]


@app.post("/api/coupons/validate", response_model=CouponValidateResponse)
async def validate_coupon(data: CouponValidateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Coupon).where(Coupon.code == data.code.upper(), Coupon.is_active.is_(True))
    )
    coupon = result.scalar_one_or_none()
    if coupon:
        if coupon.discount_type == "fixed" and coupon.discount_amount:
            return CouponValidateResponse(
                valid=True,
                discount_type="fixed",
                discount_percent=0,
                discount_amount=float(coupon.discount_amount),
                message=f"Kod rabatowy -{coupon.discount_amount} zł zastosowany!",
            )
        return CouponValidateResponse(
            valid=True,
            discount_type="percent",
            discount_percent=coupon.discount_percent,
            discount_amount=0,
            message=f"Kod rabatowy -{coupon.discount_percent}% zastosowany!",
        )
    return CouponValidateResponse(
        valid=False,
        discount_percent=0,
        message="Nieprawidłowy kod rabatowy",
    )


def _order_to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        status=order.status,
        delivery_mode=order.delivery_mode,
        first_name=order.first_name,
        last_name=order.last_name,
        phone=order.phone,
        email=order.email,
        payment_method=order.payment_method,
        coupon_code=order.coupon_code,
        scheduled_date=order.scheduled_date.isoformat() if order.scheduled_date else None,
        scheduled_time=order.scheduled_time,
        eta_minutes=order.eta_minutes,
        items_total=order.items_total,
        delivery_fee=order.delivery_fee,
        discount=order.discount,
        total=order.total,
        items=[
            OrderItemResponse(
                id=item.id,
                dish_id=item.dish_id,
                dish_name=item.dish_name,
                base_price=item.base_price,
                quantity=item.quantity,
                ingredients_snapshot=item.ingredients_snapshot,
                extras_snapshot=item.extras_snapshot,
                item_total=item.item_total,
            )
            for item in order.items
        ],
    )


# --- Reservation endpoints ---


@app.get("/api/my-reservations")
async def get_my_reservations(
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Reservation)
        .where(
            Reservation.user_id == user.id,
            Reservation.status == "confirmed",
            Reservation.reservation_date >= date.today(),
        )
        .options(selectinload(Reservation.table))
        .order_by(Reservation.reservation_date, Reservation.start_time)
    )
    return [
        {
            "id": r.id,
            "table_label": r.table.label,
            "zone": r.table.zone,
            "reservation_date": r.reservation_date.isoformat(),
            "start_time": r.start_time,
            "guests_count": r.guests_count,
            "status": r.status,
            "notes": r.notes,
        }
        for r in result.scalars().all()
    ]


@app.get("/api/tables")
async def get_tables(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RestaurantTable)
        .where(RestaurantTable.is_active.is_(True))
        .order_by(RestaurantTable.display_order)
    )
    return [
        {
            "id": t.id,
            "label": t.label,
            "seats": t.seats,
            "zone": t.zone,
            "position_x": t.position_x,
            "position_y": t.position_y,
        }
        for t in result.scalars().all()
    ]


@app.get("/api/reservations/availability")
async def get_availability(
    date_str: str,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Nieprawidłowy format daty (YYYY-MM-DD)")

    # Get reservation duration from settings
    setting = await db.execute(
        select(SiteSetting).where(SiteSetting.key == "reservation_duration")
    )
    duration_setting = setting.scalar_one_or_none()
    duration_hours = int(duration_setting.value) if duration_setting else 2

    # Get all confirmed reservations for this date
    result = await db.execute(
        select(Reservation).where(
            Reservation.reservation_date == target_date,
            Reservation.status == "confirmed",
        )
    )
    reservations = result.scalars().all()

    # Build a map: table_id -> set of blocked time slots
    blocked = {}
    for r in reservations:
        if r.table_id not in blocked:
            blocked[r.table_id] = set()
        # Parse start time and block slots for duration
        h, m = map(int, r.start_time.split(":"))
        for offset in range(duration_hours * 2):  # each slot is 30 min
            slot_min = h * 60 + m + offset * 30
            slot_h, slot_m = divmod(slot_min, 60)
            if slot_h < 24:
                blocked[r.table_id].add(f"{slot_h:02d}:{slot_m:02d}")

    # Check if logged-in user already has a reservation on this date
    user_has_reservation = False
    user_reservation_info = None
    if user:
        for r in reservations:
            if r.user_id == user.id:
                user_has_reservation = True
                user_reservation_info = {
                    "table_id": r.table_id,
                    "start_time": r.start_time,
                    "guests_count": r.guests_count,
                }
                break

    return {
        "date": date_str,
        "duration_hours": duration_hours,
        "blocked": {str(k): sorted(v) for k, v in blocked.items()},
        "user_has_reservation": user_has_reservation,
        "user_reservation": user_reservation_info,
    }


@app.post("/api/reservations", status_code=201)
async def create_reservation(
    data: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_user),
):
    table_id = data.get("table_id")
    reservation_date = data.get("date")
    start_time = data.get("start_time")
    guests_count = data.get("guests_count", 2)
    notes = data.get("notes")

    if not table_id or not reservation_date or not start_time:
        raise HTTPException(status_code=400, detail="Brakujące dane rezerwacji")

    # Validate time format (HH:MM, full or half hour)
    if start_time not in [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]:
        raise HTTPException(status_code=400, detail="Rezerwacja możliwa tylko na pełne godziny lub pół godziny")

    try:
        target_date = date.fromisoformat(reservation_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Nieprawidłowy format daty")

    if target_date < date.today():
        raise HTTPException(status_code=400, detail="Nie można rezerwować w przeszłości")

    # Limit: one reservation per user per day
    user_res = await db.execute(
        select(Reservation).where(
            Reservation.user_id == user.id,
            Reservation.reservation_date == target_date,
            Reservation.status == "confirmed",
        )
    )
    if user_res.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Masz już rezerwację na ten dzień. Możesz mieć tylko jedną rezerwację dziennie.",
        )

    # Check table exists
    table_result = await db.execute(
        select(RestaurantTable).where(RestaurantTable.id == table_id, RestaurantTable.is_active.is_(True))
    )
    table = table_result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Stolik nie znaleziony")

    # Get duration setting
    setting = await db.execute(
        select(SiteSetting).where(SiteSetting.key == "reservation_duration")
    )
    duration_setting = setting.scalar_one_or_none()
    duration_hours = int(duration_setting.value) if duration_setting else 2

    # Check for overlap: requested time must not fall in any existing reservation's blocked range,
    # AND the requested reservation must not block any existing reservation's start time
    existing = await db.execute(
        select(Reservation).where(
            Reservation.table_id == table_id,
            Reservation.reservation_date == target_date,
            Reservation.status == "confirmed",
        )
    )
    req_h, req_m = map(int, start_time.split(":"))
    req_start_min = req_h * 60 + req_m
    req_end_min = req_start_min + duration_hours * 60

    for r in existing.scalars().all():
        ex_h, ex_m = map(int, r.start_time.split(":"))
        ex_start_min = ex_h * 60 + ex_m
        ex_end_min = ex_start_min + duration_hours * 60
        if req_start_min < ex_end_min and req_end_min > ex_start_min:
            raise HTTPException(
                status_code=409,
                detail=f"Stolik {table.label} jest już zarezerwowany w tym terminie",
            )

    guest_name = user.first_name or "Gość"
    guest_phone = user.phone or ""

    reservation = Reservation(
        table_id=table_id,
        user_id=user.id,
        reservation_date=target_date,
        start_time=start_time,
        guest_name=guest_name,
        guest_phone=guest_phone,
        guests_count=guests_count,
        notes=notes,
    )
    db.add(reservation)

    # Create notification for admin
    notification = Notification(
        type="reservation",
        title=f"Nowa rezerwacja — {table.label}",
        message=(
            f"{guest_name} ({guest_phone}) zarezerwował stolik {table.label} "
            f"na {target_date.isoformat()} o {start_time}, "
            f"liczba gości: {guests_count}"
        ),
    )
    db.add(notification)

    await db.commit()
    await db.refresh(reservation)

    background_tasks.add_task(push_to_all_bg, {
        "type": "reservation",
        "id": reservation.id,
        "title": f"📅 Nowa rezerwacja — {table.label}",
        "body": f"{guest_name}, {target_date.isoformat()} o {start_time}, {guests_count} os.",
        "url": "/",
    })

    return {
        "id": reservation.id,
        "table_id": reservation.table_id,
        "table_label": table.label,
        "date": reservation.reservation_date.isoformat(),
        "start_time": reservation.start_time,
        "guests_count": reservation.guests_count,
        "status": reservation.status,
    }


@app.get("/api/order-slots")
async def get_order_slots(date_str: str, db: AsyncSession = Depends(get_db)):
    """Return count of orders per scheduled_time for a given date."""
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Nieprawidłowy format daty")

    result = await db.execute(
        select(Order.scheduled_time, func.count(Order.id))
        .where(
            Order.scheduled_date == target_date,
            Order.scheduled_time.isnot(None),
            Order.status.notin_(["cancelled"]),
        )
        .group_by(Order.scheduled_time)
    )
    slots = {row[0]: row[1] for row in result.all()}
    return {"date": date_str, "slots": slots}


@app.get("/api/event-banners")
async def get_active_banners(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EventBanner).where(EventBanner.is_active.is_(True))
        .order_by(EventBanner.created_at.desc())
    )
    return [
        {
            "id": b.id,
            "title": b.title,
            "subtitle": b.subtitle,
            "image_url": b.image_url,
            "link_url": b.link_url,
        }
        for b in result.scalars().all()
    ]


@app.get("/api/site-config")
async def get_site_config(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SiteSetting))
    settings = {s.key: s.value for s in result.scalars().all()}
    return {"phone": settings.get("phone", "+48 123 456 789")}


# --- Push notification endpoints ---


@app.get("/api/push/vapid-key")
async def get_vapid_key():
    if not VAPID_PUBLIC_KEY:
        raise HTTPException(status_code=503, detail="Powiadomienia push nie są skonfigurowane")
    return {"public_key": VAPID_PUBLIC_KEY}


@app.post("/api/push/subscribe", status_code=201)
async def push_subscribe(
    data: dict,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    endpoint = data.get("endpoint")
    p256dh = data.get("p256dh")
    auth = data.get("auth")
    if not endpoint or not p256dh or not auth:
        raise HTTPException(status_code=400, detail="Brakujące dane subskrypcji")

    # Upsert — update keys if endpoint already known
    result = await db.execute(select(PushSubscription).where(PushSubscription.endpoint == endpoint))
    sub = result.scalar_one_or_none()
    if sub:
        sub.p256dh = p256dh
        sub.auth = auth
        sub.user_id = user.id
    else:
        db.add(PushSubscription(user_id=user.id, endpoint=endpoint, p256dh=p256dh, auth=auth))

    await db.commit()
    return {"ok": True}


@app.post("/api/push/unsubscribe", status_code=204)
async def push_unsubscribe(
    data: dict,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    endpoint = data.get("endpoint")
    if not endpoint:
        return
    result = await db.execute(
        select(PushSubscription).where(
            PushSubscription.endpoint == endpoint,
            PushSubscription.user_id == user.id,
        )
    )
    sub = result.scalar_one_or_none()
    if sub:
        await db.delete(sub)
        await db.commit()


# --- AutoPay payment endpoints ---


@app.post("/api/payments/autopay/initiate/{order_id}")
async def autopay_initiate(order_id: int, db: AsyncSession = Depends(get_db)):
    """
    Return the gateway URL and POST parameters the frontend needs to redirect
    the customer to AutoPay for payment.

    The frontend should create a hidden HTML form, populate it with `params`,
    and submit it to `gateway_url`.
    """
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Zamówienie nie istnieje")
    if order.payment_method not in ONLINE_PAYMENT_METHODS:
        raise HTTPException(status_code=400, detail="To zamówienie nie wymaga płatności online")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Zamówienie jest już przetworzone")

    amount = f"{order.total:.2f}"
    params = build_payment_params(order_id=order.id, amount=amount)

    return {"gateway_url": AUTOPAY_GATEWAY_URL, "params": params}


@app.post("/api/payments/autopay/itn")
async def autopay_itn(request: Request, db: AsyncSession = Depends(get_db)):
    """
    ITN (Instant Transaction Notification) webhook called by AutoPay to confirm
    payment status. Expects a form-encoded body with a `transactions` field
    containing a Base64-encoded XML document.

    Responds with an XML confirmation (CONFIRMED / NOTCONFIRMED) as required
    by AutoPay. Must return HTTP 200 — otherwise AutoPay will retry.
    """
    form = await request.form()
    raw_b64 = form.get("transactions")

    if not raw_b64:
        xml_err = build_confirmation_xml("", "", False)
        return Response(content=xml_err, media_type="application/xml")

    try:
        raw_xml = b64decode(raw_b64).decode("utf-8")
        tx = parse_itn(raw_xml)
    except Exception:
        xml_err = build_confirmation_xml("", "", False)
        return Response(content=xml_err, media_type="application/xml")

    service_id = tx["service_id"]
    order_id_str = tx["order_id"]
    confirmed = False

    if verify_itn_hash(tx):
        if tx["payment_status"] == "SUCCESS":
            try:
                order = await db.get(Order, int(order_id_str))
                if order and order.status == "pending":
                    order.status = "confirmed"
                    await db.commit()
                confirmed = True
            except Exception:
                pass
        elif tx["payment_status"] == "FAILURE":
            try:
                order = await db.get(Order, int(order_id_str))
                if order and order.status == "pending":
                    order.status = "cancelled"
                    await db.commit()
            except Exception:
                pass
            confirmed = True  # hash was valid, we just won't fulfill the order

    xml_response = build_confirmation_xml(service_id, order_id_str, confirmed)
    return Response(content=xml_response, media_type="application/xml")


@app.get("/")
def read_root():
    return {"Hello": "World"}
