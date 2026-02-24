import pytest
from conftest import auth_header


ADDR_DATA = {
    "label": "Dom",
    "city": "Piaseczno",
    "street": "Sierakowskiego",
    "house_number": "2",
    "apartment": "10",
}


# --- Create address ---


async def test_create_address(client, registered_user):
    _, token = registered_user
    res = await client.post(
        "/api/auth/addresses", json=ADDR_DATA, headers=auth_header(token),
    )
    assert res.status_code == 201
    data = res.json()
    assert data["city"] == "Piaseczno"
    assert data["label"] == "Dom"
    assert "id" in data


async def test_create_address_unauthenticated(client):
    res = await client.post("/api/auth/addresses", json=ADDR_DATA)
    assert res.status_code == 401


# --- List addresses ---


async def test_list_addresses_empty(client, registered_user):
    _, token = registered_user
    res = await client.get("/api/auth/addresses", headers=auth_header(token))
    assert res.status_code == 200
    assert res.json() == []


async def test_list_addresses_after_create(client, registered_user):
    _, token = registered_user
    await client.post("/api/auth/addresses", json=ADDR_DATA, headers=auth_header(token))
    await client.post(
        "/api/auth/addresses",
        json={**ADDR_DATA, "label": "Praca", "city": "Warszawa"},
        headers=auth_header(token),
    )
    res = await client.get("/api/auth/addresses", headers=auth_header(token))
    assert res.status_code == 200
    assert len(res.json()) == 2


# --- Update address ---


async def test_update_address(client, registered_user):
    _, token = registered_user
    create = await client.post(
        "/api/auth/addresses", json=ADDR_DATA, headers=auth_header(token),
    )
    addr_id = create.json()["id"]

    res = await client.patch(
        f"/api/auth/addresses/{addr_id}",
        json={"city": "Warszawa", "label": "Biuro"},
        headers=auth_header(token),
    )
    assert res.status_code == 200
    data = res.json()
    assert data["city"] == "Warszawa"
    assert data["label"] == "Biuro"
    assert data["street"] == "Sierakowskiego"  # unchanged


async def test_update_address_not_found(client, registered_user):
    _, token = registered_user
    res = await client.patch(
        "/api/auth/addresses/9999",
        json={"city": "Kraków"},
        headers=auth_header(token),
    )
    assert res.status_code == 404


# --- Delete address ---


async def test_delete_address(client, registered_user):
    _, token = registered_user
    create = await client.post(
        "/api/auth/addresses", json=ADDR_DATA, headers=auth_header(token),
    )
    addr_id = create.json()["id"]

    res = await client.delete(
        f"/api/auth/addresses/{addr_id}", headers=auth_header(token),
    )
    assert res.status_code == 204

    listing = await client.get("/api/auth/addresses", headers=auth_header(token))
    assert len(listing.json()) == 0


async def test_delete_address_not_found(client, registered_user):
    _, token = registered_user
    res = await client.delete(
        "/api/auth/addresses/9999", headers=auth_header(token),
    )
    assert res.status_code == 404


# --- Isolation: user A can't see/edit user B's addresses ---


async def test_address_isolation(client, registered_user, admin_user):
    _, user_token = registered_user
    _, admin_token = admin_user

    # User creates address
    create = await client.post(
        "/api/auth/addresses", json=ADDR_DATA, headers=auth_header(user_token),
    )
    addr_id = create.json()["id"]

    # Admin can't see it
    listing = await client.get("/api/auth/addresses", headers=auth_header(admin_token))
    assert len(listing.json()) == 0

    # Admin can't update it
    res = await client.patch(
        f"/api/auth/addresses/{addr_id}",
        json={"city": "Hack"},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 404

    # Admin can't delete it
    res = await client.delete(
        f"/api/auth/addresses/{addr_id}", headers=auth_header(admin_token),
    )
    assert res.status_code == 404
