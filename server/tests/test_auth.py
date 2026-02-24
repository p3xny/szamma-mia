import pytest
from conftest import auth_header


# --- Registration ---


async def test_register_success(client):
    res = await client.post("/api/auth/register", json={
        "email": "new@test.pl",
        "first_name": "Anna",
        "phone": "111222333",
        "password": "secret123",
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_register_duplicate_email(client, registered_user):
    res = await client.post("/api/auth/register", json={
        "email": "user@test.pl",
        "first_name": "Kopia",
        "phone": "999888777",
        "password": "secret123",
    })
    assert res.status_code == 409


async def test_register_invalid_email(client):
    res = await client.post("/api/auth/register", json={
        "email": "not-an-email",
        "first_name": "Test",
        "phone": "111",
        "password": "secret123",
    })
    assert res.status_code == 422


# --- Login ---


async def test_login_success(client, registered_user):
    res = await client.post("/api/auth/login", json={
        "email": "user@test.pl",
        "password": "haslo123",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


async def test_login_wrong_password(client, registered_user):
    res = await client.post("/api/auth/login", json={
        "email": "user@test.pl",
        "password": "wrong",
    })
    assert res.status_code == 401


async def test_login_nonexistent_email(client):
    res = await client.post("/api/auth/login", json={
        "email": "nobody@test.pl",
        "password": "anything",
    })
    assert res.status_code == 401


# --- Profile (GET /api/auth/me) ---


async def test_get_me_authenticated(client, registered_user):
    user, token = registered_user
    res = await client.get("/api/auth/me", headers=auth_header(token))
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "user@test.pl"
    assert data["first_name"] == "Jan"
    assert data["role"] == "user"


async def test_get_me_unauthenticated(client):
    res = await client.get("/api/auth/me")
    assert res.status_code == 401


async def test_get_me_invalid_token(client):
    res = await client.get("/api/auth/me", headers=auth_header("garbage-token"))
    assert res.status_code == 401


# --- Profile update (PATCH /api/auth/me) ---


async def test_update_profile(client, registered_user):
    user, token = registered_user
    res = await client.patch(
        "/api/auth/me",
        json={"first_name": "Janek", "phone": "987654321"},
        headers=auth_header(token),
    )
    assert res.status_code == 200
    data = res.json()
    assert data["first_name"] == "Janek"
    assert data["phone"] == "987654321"
    assert data["email"] == "user@test.pl"  # unchanged


async def test_update_email_conflict(client, registered_user, admin_user):
    _, token = registered_user
    res = await client.patch(
        "/api/auth/me",
        json={"email": "admin@test.pl"},
        headers=auth_header(token),
    )
    assert res.status_code == 409


async def test_update_profile_unauthenticated(client):
    res = await client.patch("/api/auth/me", json={"first_name": "X"})
    assert res.status_code == 401


# --- Register then immediately use token ---


async def test_register_token_works(client):
    reg = await client.post("/api/auth/register", json={
        "email": "fresh@test.pl",
        "first_name": "Fresh",
        "phone": "555666777",
        "password": "pass1234",
    })
    token = reg.json()["access_token"]
    me = await client.get("/api/auth/me", headers=auth_header(token))
    assert me.status_code == 200
    assert me.json()["email"] == "fresh@test.pl"
