import pytest
from conftest import auth_header


def order_payload(dish_id, **overrides):
    base = {
        "delivery_mode": "delivery",
        "first_name": "Jan",
        "phone": "123456789",
        "city": "Piaseczno",
        "street": "Sierakowskiego",
        "house_number": "2",
        "payment_method": "cash",
        "items": [{"dish_id": dish_id, "quantity": 2}],
    }
    base.update(overrides)
    return base


# --- Guest checkout ---


async def test_create_order_guest(client, seed_menu):
    dish = seed_menu
    res = await client.post("/api/orders", json=order_payload(dish.id))
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "pending"
    assert float(data["total"]) == 60  # 30 * 2


async def test_create_order_empty_items(client, seed_menu):
    res = await client.post("/api/orders", json=order_payload(seed_menu.id, items=[]))
    assert res.status_code == 400


async def test_create_order_below_minimum(client, seed_menu):
    dish = seed_menu
    res = await client.post(
        "/api/orders",
        json=order_payload(dish.id, items=[{"dish_id": dish.id, "quantity": 1}]),
    )
    assert res.status_code == 400
    assert "50" in res.json()["detail"]


async def test_create_order_delivery_missing_address(client, seed_menu):
    dish = seed_menu
    res = await client.post(
        "/api/orders",
        json=order_payload(dish.id, city=None, street=None, house_number=None),
    )
    assert res.status_code == 400


async def test_create_order_pickup_no_address_needed(client, seed_menu):
    dish = seed_menu
    res = await client.post(
        "/api/orders",
        json=order_payload(
            dish.id,
            delivery_mode="pickup",
            city=None, street=None, house_number=None,
        ),
    )
    assert res.status_code == 201


async def test_create_order_nonexistent_dish(client, seed_menu):
    res = await client.post("/api/orders", json=order_payload(99999))
    assert res.status_code == 400


# --- Authenticated order ---


async def test_create_order_authenticated(client, seed_menu, registered_user):
    dish = seed_menu
    _, token = registered_user
    res = await client.post(
        "/api/orders",
        json=order_payload(dish.id),
        headers=auth_header(token),
    )
    assert res.status_code == 201


# --- Get order ---


async def test_get_order(client, seed_menu):
    dish = seed_menu
    create = await client.post("/api/orders", json=order_payload(dish.id))
    order_id = create.json()["id"]

    res = await client.get(f"/api/orders/{order_id}")
    assert res.status_code == 200
    assert res.json()["id"] == order_id


async def test_get_order_not_found(client):
    res = await client.get("/api/orders/99999")
    assert res.status_code == 404


# --- Coupon ---


async def test_create_order_with_coupon(client, seed_menu):
    dish = seed_menu
    res = await client.post(
        "/api/orders",
        json=order_payload(dish.id, coupon_code="SZAMMA10"),
    )
    assert res.status_code == 201
    data = res.json()
    assert float(data["discount"]) == 6  # 10% of 60 = 6
    assert float(data["total"]) == 54


# --- Coupon validation ---


async def test_validate_coupon_valid(client, seed_coupon):
    res = await client.post("/api/coupons/validate", json={"code": "SZAMMA10"})
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["discount_percent"] == 10


async def test_validate_coupon_invalid(client):
    res = await client.post("/api/coupons/validate", json={"code": "FAKE"})
    assert res.status_code == 200
    assert res.json()["valid"] is False


# --- Menu & Categories ---


async def test_get_menu(client, seed_menu):
    res = await client.get("/api/menu")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["name"] == "Margherita"
    assert data[0]["category"] == "pizza"
    assert len(data[0]["ingredients"]) == 1
    assert len(data[0]["extras"]) == 1


async def test_get_categories(client, seed_menu):
    res = await client.get("/api/categories")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["key"] == "pizza"


async def test_get_menu_empty(client):
    res = await client.get("/api/menu")
    assert res.status_code == 200
    assert res.json() == []
