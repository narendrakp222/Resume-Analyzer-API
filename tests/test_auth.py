import pytest


@pytest.mark.asyncio
async def test_register_user_success(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    user_data = {
        "username": "bob",
        "email": "bob@example.com",
        "password": "Password123"
    }
    res1 = await client.post("/auth/register", json=user_data)
    assert res1.status_code == 201

    user_data2 = {
        "username": "bob_new",
        "email": "bob@example.com",
        "password": "Password123"
    }
    res2 = await client.post("/auth/register", json=user_data2)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client):
    user_data = {
        "username": "charlie",
        "email": "charlie@example.com",
        "password": "Password123"
    }
    await client.post("/auth/register", json=user_data)

    login_res = await client.post(
        "/auth/login",
        json={
            "username_or_email": "charlie",
            "password": "Password123"
        }
    )
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(client):
    user_data = {
        "username": "dave",
        "email": "dave@example.com",
        "password": "Password123"
    }
    await client.post("/auth/register", json=user_data)

    login_res = await client.post(
        "/auth/login",
        json={
            "username_or_email": "dave",
            "password": "WrongPassword"
        }
    )
    assert login_res.status_code == 401
