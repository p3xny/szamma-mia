from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from admin_schemas import (
    AdminOrderItemResponse,
    AdminOrderResponse,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    CouponCreate,
    CouponResponse,
    CouponUpdate,
    DishCreate,
    DishExtraCreate,
    DishExtraResponse,
    DishExtraUpdate,
    DishIngredientCreate,
    DishIngredientResponse,
    DishIngredientUpdate,
    DishResponse,
    DishUpdate,
    EventBannerCreate,
    EventBannerResponse,
    EventBannerUpdate,
    ExtraCreate,
    ExtraResponse,
    IngredientCreate,
    IngredientResponse,
    NotificationResponse,
    OrderStatusUpdate,
    ReservationResponse,
    ReservationUpdate,
    SettingsResponse,
    SettingsUpdate,
    TableCreate,
    TableResponse,
    TableUpdate,
)
from auth import require_admin
from database import get_db
from models import (
    Category,
    Coupon,
    Dish,
    DishExtra,
    DishIngredient,
    EventBanner,
    Extra,
    Ingredient,
    Notification,
    Order,
    OrderItem,
    Reservation,
    RestaurantTable,
    SiteSetting,
    User,
)

router = APIRouter(prefix="/api/admin", dependencies=[Depends(require_admin)])


# --- Helper ---


def _dish_to_response(dish: Dish) -> DishResponse:
    return DishResponse(
        id=dish.id,
        name=dish.name,
        category_id=dish.category_id,
        category_label=dish.category.label,
        base_price=dish.base_price,
        original_price=dish.original_price,
        image_url=dish.image_url,
        is_daily_special=dish.is_daily_special,
        is_active=dish.is_active,
        display_order=dish.display_order,
        ingredients=[
            DishIngredientResponse(
                id=di.id,
                ingredient_id=di.ingredient_id,
                ingredient_name=di.ingredient.name,
                is_included_by_default=di.is_included_by_default,
                additional_price=di.additional_price,
                display_order=di.display_order,
            )
            for di in sorted(dish.dish_ingredients, key=lambda x: x.display_order)
        ],
        extras=[
            DishExtraResponse(
                id=de.id,
                extra_id=de.extra_id,
                extra_name=de.extra.name,
                price=de.price,
                display_order=de.display_order,
            )
            for de in sorted(dish.dish_extras, key=lambda x: x.display_order)
        ],
    )


async def _get_dish_loaded(dish_id: int, db: AsyncSession) -> Dish:
    result = await db.execute(
        select(Dish)
        .where(Dish.id == dish_id)
        .options(
            selectinload(Dish.category),
            selectinload(Dish.dish_ingredients).selectinload(DishIngredient.ingredient),
            selectinload(Dish.dish_extras).selectinload(DishExtra.extra),
        )
    )
    dish = result.scalar_one_or_none()
    if not dish:
        raise HTTPException(status_code=404, detail="Danie nie znalezione")
    return dish


# --- Dishes ---


@router.get("/dishes", response_model=list[DishResponse])
async def list_dishes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Dish)
        .options(
            selectinload(Dish.category),
            selectinload(Dish.dish_ingredients).selectinload(DishIngredient.ingredient),
            selectinload(Dish.dish_extras).selectinload(DishExtra.extra),
        )
        .order_by(Dish.category_id, Dish.display_order)
    )
    return [_dish_to_response(d) for d in result.scalars().all()]


@router.post("/dishes", status_code=201, response_model=DishResponse)
async def create_dish(data: DishCreate, db: AsyncSession = Depends(get_db)):
    dish = Dish(
        name=data.name,
        category_id=data.category_id,
        base_price=data.base_price,
        original_price=data.original_price,
        image_url=data.image_url,
        is_daily_special=data.is_daily_special,
        is_active=data.is_active,
        display_order=data.display_order,
    )
    db.add(dish)
    await db.commit()
    return _dish_to_response(await _get_dish_loaded(dish.id, db))


@router.patch("/dishes/{dish_id}", response_model=DishResponse)
async def update_dish(dish_id: int, data: DishUpdate, db: AsyncSession = Depends(get_db)):
    dish = await _get_dish_loaded(dish_id, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(dish, field, value)
    await db.commit()
    return _dish_to_response(await _get_dish_loaded(dish_id, db))


@router.delete("/dishes/{dish_id}", status_code=204)
async def delete_dish(dish_id: int, db: AsyncSession = Depends(get_db)):
    dish = await _get_dish_loaded(dish_id, db)
    await db.delete(dish)
    await db.commit()


# --- Dish ingredients ---


@router.post("/dishes/{dish_id}/ingredients", status_code=201, response_model=DishIngredientResponse)
async def add_dish_ingredient(
    dish_id: int, data: DishIngredientCreate, db: AsyncSession = Depends(get_db)
):
    await _get_dish_loaded(dish_id, db)
    result = await db.execute(
        select(Ingredient).where(Ingredient.id == data.ingredient_id)
    )
    ingredient = result.scalar_one_or_none()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Składnik nie znaleziony")

    di = DishIngredient(
        dish_id=dish_id,
        ingredient_id=data.ingredient_id,
        is_included_by_default=data.is_included_by_default,
        additional_price=data.additional_price,
        display_order=data.display_order,
    )
    db.add(di)
    await db.commit()
    await db.refresh(di)

    return DishIngredientResponse(
        id=di.id,
        ingredient_id=di.ingredient_id,
        ingredient_name=ingredient.name,
        is_included_by_default=di.is_included_by_default,
        additional_price=di.additional_price,
        display_order=di.display_order,
    )


@router.patch("/dishes/{dish_id}/ingredients/{di_id}", response_model=DishIngredientResponse)
async def update_dish_ingredient(
    dish_id: int, di_id: int, data: DishIngredientUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DishIngredient)
        .where(DishIngredient.id == di_id, DishIngredient.dish_id == dish_id)
        .options(selectinload(DishIngredient.ingredient))
    )
    di = result.scalar_one_or_none()
    if not di:
        raise HTTPException(status_code=404, detail="Składnik dania nie znaleziony")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(di, field, value)
    await db.commit()
    await db.refresh(di)

    return DishIngredientResponse(
        id=di.id,
        ingredient_id=di.ingredient_id,
        ingredient_name=di.ingredient.name,
        is_included_by_default=di.is_included_by_default,
        additional_price=di.additional_price,
        display_order=di.display_order,
    )


@router.delete("/dishes/{dish_id}/ingredients/{di_id}", status_code=204)
async def delete_dish_ingredient(
    dish_id: int, di_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DishIngredient).where(DishIngredient.id == di_id, DishIngredient.dish_id == dish_id)
    )
    di = result.scalar_one_or_none()
    if not di:
        raise HTTPException(status_code=404, detail="Składnik dania nie znaleziony")

    await db.delete(di)
    await db.commit()


# --- Dish extras ---


@router.post("/dishes/{dish_id}/extras", status_code=201, response_model=DishExtraResponse)
async def add_dish_extra(
    dish_id: int, data: DishExtraCreate, db: AsyncSession = Depends(get_db)
):
    await _get_dish_loaded(dish_id, db)
    result = await db.execute(select(Extra).where(Extra.id == data.extra_id))
    extra = result.scalar_one_or_none()
    if not extra:
        raise HTTPException(status_code=404, detail="Dodatek nie znaleziony")

    de = DishExtra(
        dish_id=dish_id,
        extra_id=data.extra_id,
        price=data.price,
        display_order=data.display_order,
    )
    db.add(de)
    await db.commit()
    await db.refresh(de)

    return DishExtraResponse(
        id=de.id,
        extra_id=de.extra_id,
        extra_name=extra.name,
        price=de.price,
        display_order=de.display_order,
    )


@router.patch("/dishes/{dish_id}/extras/{de_id}", response_model=DishExtraResponse)
async def update_dish_extra(
    dish_id: int, de_id: int, data: DishExtraUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DishExtra)
        .where(DishExtra.id == de_id, DishExtra.dish_id == dish_id)
        .options(selectinload(DishExtra.extra))
    )
    de = result.scalar_one_or_none()
    if not de:
        raise HTTPException(status_code=404, detail="Dodatek dania nie znaleziony")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(de, field, value)
    await db.commit()
    await db.refresh(de)

    return DishExtraResponse(
        id=de.id,
        extra_id=de.extra_id,
        extra_name=de.extra.name,
        price=de.price,
        display_order=de.display_order,
    )


@router.delete("/dishes/{dish_id}/extras/{de_id}", status_code=204)
async def delete_dish_extra(
    dish_id: int, de_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DishExtra).where(DishExtra.id == de_id, DishExtra.dish_id == dish_id)
    )
    de = result.scalar_one_or_none()
    if not de:
        raise HTTPException(status_code=404, detail="Dodatek dania nie znaleziony")

    await db.delete(de)
    await db.commit()


# --- Categories ---


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).order_by(Category.display_order))
    return [
        CategoryResponse(
            id=c.id, key=c.key, label=c.label,
            display_order=c.display_order, is_active=c.is_active,
        )
        for c in result.scalars().all()
    ]


@router.post("/categories", status_code=201, response_model=CategoryResponse)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    cat = Category(
        key=data.key, label=data.label,
        display_order=data.display_order, is_active=data.is_active,
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return CategoryResponse(
        id=cat.id, key=cat.key, label=cat.label,
        display_order=cat.display_order, is_active=cat.is_active,
    )


@router.patch("/categories/{cat_id}", response_model=CategoryResponse)
async def update_category(
    cat_id: int, data: CategoryUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Category).where(Category.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Kategoria nie znaleziona")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    await db.commit()
    await db.refresh(cat)
    return CategoryResponse(
        id=cat.id, key=cat.key, label=cat.label,
        display_order=cat.display_order, is_active=cat.is_active,
    )


@router.delete("/categories/{cat_id}", status_code=204)
async def delete_category(cat_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Kategoria nie znaleziona")

    await db.delete(cat)
    await db.commit()


# --- Ingredients (master list) ---


@router.get("/ingredients", response_model=list[IngredientResponse])
async def list_ingredients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ingredient).order_by(Ingredient.name))
    return [
        IngredientResponse(id=i.id, name=i.name, is_active=i.is_active)
        for i in result.scalars().all()
    ]


@router.post("/ingredients", status_code=201, response_model=IngredientResponse)
async def create_ingredient(data: IngredientCreate, db: AsyncSession = Depends(get_db)):
    ing = Ingredient(name=data.name)
    db.add(ing)
    await db.commit()
    await db.refresh(ing)
    return IngredientResponse(id=ing.id, name=ing.name, is_active=ing.is_active)


# --- Extras (master list) ---


@router.get("/extras", response_model=list[ExtraResponse])
async def list_extras(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Extra).order_by(Extra.name))
    return [
        ExtraResponse(id=e.id, name=e.name, is_active=e.is_active)
        for e in result.scalars().all()
    ]


@router.post("/extras", status_code=201, response_model=ExtraResponse)
async def create_extra(data: ExtraCreate, db: AsyncSession = Depends(get_db)):
    ext = Extra(name=data.name)
    db.add(ext)
    await db.commit()
    await db.refresh(ext)
    return ExtraResponse(id=ext.id, name=ext.name, is_active=ext.is_active)


# --- Coupons ---


@router.get("/coupons", response_model=list[CouponResponse])
async def list_coupons(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Coupon).order_by(Coupon.created_at.desc()))
    return [
        CouponResponse(
            id=c.id, code=c.code, discount_type=c.discount_type,
            discount_percent=c.discount_percent, discount_amount=c.discount_amount,
            is_active=c.is_active,
        )
        for c in result.scalars().all()
    ]


@router.post("/coupons", status_code=201, response_model=CouponResponse)
async def create_coupon(data: CouponCreate, db: AsyncSession = Depends(get_db)):
    coupon = Coupon(
        code=data.code.upper(),
        discount_type=data.discount_type,
        discount_percent=data.discount_percent,
        discount_amount=data.discount_amount,
        is_active=data.is_active,
    )
    db.add(coupon)
    await db.commit()
    await db.refresh(coupon)
    return CouponResponse(
        id=coupon.id, code=coupon.code, discount_type=coupon.discount_type,
        discount_percent=coupon.discount_percent, discount_amount=coupon.discount_amount,
        is_active=coupon.is_active,
    )


@router.patch("/coupons/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: int, data: CouponUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Kupon nie znaleziony")

    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "code" and value is not None:
            value = value.upper()
        setattr(coupon, field, value)
    await db.commit()
    await db.refresh(coupon)
    return CouponResponse(
        id=coupon.id, code=coupon.code, discount_type=coupon.discount_type,
        discount_percent=coupon.discount_percent, discount_amount=coupon.discount_amount,
        is_active=coupon.is_active,
    )


@router.delete("/coupons/{coupon_id}", status_code=204)
async def delete_coupon(coupon_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Kupon nie znaleziony")

    await db.delete(coupon)
    await db.commit()


# --- Event banners ---


@router.get("/event-banners", response_model=list[EventBannerResponse])
async def list_event_banners(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EventBanner).order_by(EventBanner.created_at.desc()))
    return [
        EventBannerResponse(
            id=b.id, title=b.title, subtitle=b.subtitle,
            image_url=b.image_url, link_url=b.link_url, is_active=b.is_active,
        )
        for b in result.scalars().all()
    ]


@router.post("/event-banners", status_code=201, response_model=EventBannerResponse)
async def create_event_banner(data: EventBannerCreate, db: AsyncSession = Depends(get_db)):
    banner = EventBanner(
        title=data.title, subtitle=data.subtitle,
        image_url=data.image_url, link_url=data.link_url, is_active=data.is_active,
    )
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return EventBannerResponse(
        id=banner.id, title=banner.title, subtitle=banner.subtitle,
        image_url=banner.image_url, link_url=banner.link_url, is_active=banner.is_active,
    )


@router.patch("/event-banners/{banner_id}", response_model=EventBannerResponse)
async def update_event_banner(
    banner_id: int, data: EventBannerUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(EventBanner).where(EventBanner.id == banner_id))
    banner = result.scalar_one_or_none()
    if not banner:
        raise HTTPException(status_code=404, detail="Baner nie znaleziony")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(banner, field, value)
    await db.commit()
    await db.refresh(banner)
    return EventBannerResponse(
        id=banner.id, title=banner.title, subtitle=banner.subtitle,
        image_url=banner.image_url, link_url=banner.link_url, is_active=banner.is_active,
    )


@router.delete("/event-banners/{banner_id}", status_code=204)
async def delete_event_banner(banner_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EventBanner).where(EventBanner.id == banner_id))
    banner = result.scalar_one_or_none()
    if not banner:
        raise HTTPException(status_code=404, detail="Baner nie znaleziony")
    await db.delete(banner)
    await db.commit()


# --- Site settings ---


# --- Tables ---


@router.get("/tables", response_model=list[TableResponse])
async def list_tables(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RestaurantTable).order_by(RestaurantTable.display_order))
    return [
        TableResponse(
            id=t.id, label=t.label, seats=t.seats, zone=t.zone,
            position_x=t.position_x, position_y=t.position_y,
            is_active=t.is_active, display_order=t.display_order,
        )
        for t in result.scalars().all()
    ]


@router.post("/tables", status_code=201, response_model=TableResponse)
async def create_table(data: TableCreate, db: AsyncSession = Depends(get_db)):
    t = RestaurantTable(
        label=data.label, seats=data.seats, zone=data.zone,
        position_x=data.position_x, position_y=data.position_y,
        is_active=data.is_active, display_order=data.display_order,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return TableResponse(
        id=t.id, label=t.label, seats=t.seats, zone=t.zone,
        position_x=t.position_x, position_y=t.position_y,
        is_active=t.is_active, display_order=t.display_order,
    )


@router.patch("/tables/{table_id}", response_model=TableResponse)
async def update_table(table_id: int, data: TableUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RestaurantTable).where(RestaurantTable.id == table_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Stolik nie znaleziony")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    await db.commit()
    await db.refresh(t)
    return TableResponse(
        id=t.id, label=t.label, seats=t.seats, zone=t.zone,
        position_x=t.position_x, position_y=t.position_y,
        is_active=t.is_active, display_order=t.display_order,
    )


@router.delete("/tables/{table_id}", status_code=204)
async def delete_table(table_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RestaurantTable).where(RestaurantTable.id == table_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Stolik nie znaleziony")
    await db.delete(t)
    await db.commit()


# --- Orders ---


@router.get("/orders", response_model=list[AdminOrderResponse])
async def list_orders(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    if status:
        query = query.where(Order.status == status)
    result = await db.execute(query)
    return [
        AdminOrderResponse(
            id=o.id,
            status=o.status,
            delivery_mode=o.delivery_mode,
            first_name=o.first_name,
            last_name=o.last_name,
            phone=o.phone,
            email=o.email,
            city=o.city,
            street=o.street,
            house_number=o.house_number,
            apartment=o.apartment,
            notes=o.notes,
            payment_method=o.payment_method,
            coupon_code=o.coupon_code,
            scheduled_date=o.scheduled_date.isoformat() if o.scheduled_date else None,
            scheduled_time=o.scheduled_time,
            eta_minutes=o.eta_minutes,
            items_total=o.items_total,
            delivery_fee=o.delivery_fee,
            discount=o.discount,
            total=o.total,
            created_at=o.created_at.isoformat() if o.created_at else "",
            items=[
                AdminOrderItemResponse(
                    id=item.id,
                    dish_id=item.dish_id,
                    dish_name=item.dish_name,
                    base_price=item.base_price,
                    quantity=item.quantity,
                    ingredients_snapshot=item.ingredients_snapshot,
                    extras_snapshot=item.extras_snapshot,
                    item_total=item.item_total,
                )
                for item in o.items
            ],
        )
        for o in result.scalars().all()
    ]


@router.patch("/orders/{order_id}", response_model=AdminOrderResponse)
async def update_order_status(
    order_id: int, data: OrderStatusUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    )
    o = result.scalar_one_or_none()
    if not o:
        raise HTTPException(status_code=404, detail="Zamówienie nie znalezione")
    o.status = data.status
    if data.eta_minutes is not None:
        o.eta_minutes = data.eta_minutes
    await db.commit()
    await db.refresh(o)
    return AdminOrderResponse(
        id=o.id,
        status=o.status,
        delivery_mode=o.delivery_mode,
        first_name=o.first_name,
        last_name=o.last_name,
        phone=o.phone,
        email=o.email,
        city=o.city,
        street=o.street,
        house_number=o.house_number,
        apartment=o.apartment,
        notes=o.notes,
        payment_method=o.payment_method,
        coupon_code=o.coupon_code,
        scheduled_date=o.scheduled_date.isoformat() if o.scheduled_date else None,
        scheduled_time=o.scheduled_time,
        items_total=o.items_total,
        delivery_fee=o.delivery_fee,
        discount=o.discount,
        total=o.total,
        created_at=o.created_at.isoformat() if o.created_at else "",
        items=[
            AdminOrderItemResponse(
                id=item.id,
                dish_id=item.dish_id,
                dish_name=item.dish_name,
                base_price=item.base_price,
                quantity=item.quantity,
                ingredients_snapshot=item.ingredients_snapshot,
                extras_snapshot=item.extras_snapshot,
                item_total=item.item_total,
            )
            for item in o.items
        ],
    )


# --- Reservations ---


@router.get("/reservations", response_model=list[ReservationResponse])
async def list_reservations(
    status: str | None = None,
    date_from: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    from datetime import date as date_type
    query = select(Reservation).options(
        selectinload(Reservation.table)
    ).order_by(Reservation.reservation_date.desc(), Reservation.start_time.desc())
    if status:
        query = query.where(Reservation.status == status)
    if date_from:
        query = query.where(Reservation.reservation_date >= date_type.fromisoformat(date_from))
    result = await db.execute(query)
    return [
        ReservationResponse(
            id=r.id, table_id=r.table_id, table_label=r.table.label,
            user_id=r.user_id, guest_name=r.guest_name, guest_phone=r.guest_phone,
            reservation_date=r.reservation_date.isoformat(),
            start_time=r.start_time, guests_count=r.guests_count,
            status=r.status, notes=r.notes,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in result.scalars().all()
    ]


@router.patch("/reservations/{res_id}", response_model=ReservationResponse)
async def update_reservation(
    res_id: int, data: ReservationUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Reservation).where(Reservation.id == res_id)
        .options(selectinload(Reservation.table))
    )
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Rezerwacja nie znaleziona")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    await db.commit()
    await db.refresh(r)
    return ReservationResponse(
        id=r.id, table_id=r.table_id, table_label=r.table.label,
        user_id=r.user_id, guest_name=r.guest_name, guest_phone=r.guest_phone,
        reservation_date=r.reservation_date.isoformat(),
        start_time=r.start_time, guests_count=r.guests_count,
        status=r.status, notes=r.notes,
        created_at=r.created_at.isoformat() if r.created_at else "",
    )


@router.delete("/reservations/{res_id}", status_code=204)
async def delete_reservation(res_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Reservation).where(Reservation.id == res_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Rezerwacja nie znaleziona")
    await db.delete(r)
    await db.commit()


# --- Notifications ---


@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(unread_only: bool = False, db: AsyncSession = Depends(get_db)):
    query = select(Notification).order_by(Notification.created_at.desc())
    if unread_only:
        query = query.where(Notification.is_read.is_(False))
    result = await db.execute(query)
    return [
        NotificationResponse(
            id=n.id, type=n.type, title=n.title, message=n.message,
            is_read=n.is_read,
            created_at=n.created_at.isoformat() if n.created_at else "",
        )
        for n in result.scalars().all()
    ]


@router.patch("/notifications/{notif_id}")
async def mark_notification_read(notif_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.id == notif_id))
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Powiadomienie nie znalezione")
    n.is_read = True
    await db.commit()
    return {"ok": True}


@router.post("/notifications/read-all")
async def mark_all_read(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.is_read.is_(False)))
    for n in result.scalars().all():
        n.is_read = True
    await db.commit()
    return {"ok": True}


# --- Site settings ---


@router.get("/settings", response_model=SettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SiteSetting))
    settings = {s.key: s.value for s in result.scalars().all()}
    return SettingsResponse(
        phone=settings.get("phone", ""),
        reservation_duration=settings.get("reservation_duration", "2"),
        eta_step=settings.get("eta_step", "10"),
        eta_default=settings.get("eta_default", "40"),
    )


@router.patch("/settings", response_model=SettingsResponse)
async def update_settings(data: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        result = await db.execute(select(SiteSetting).where(SiteSetting.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
        else:
            db.add(SiteSetting(key=key, value=value))
    await db.commit()

    result = await db.execute(select(SiteSetting))
    settings = {s.key: s.value for s in result.scalars().all()}
    return SettingsResponse(
        phone=settings.get("phone", ""),
        reservation_duration=settings.get("reservation_duration", "2"),
        eta_step=settings.get("eta_step", "10"),
        eta_default=settings.get("eta_default", "40"),
    )
