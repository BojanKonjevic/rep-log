from httpx import AsyncClient

TEST_USER = {"email": "test@example.com", "password": "testpassword123"}


async def test_register(anon_client: AsyncClient) -> None:
    resp = await anon_client.post("/auth/register", json=TEST_USER)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == TEST_USER["email"]
    assert data["is_active"] is True
    assert "id" in data


async def test_register_duplicate_returns_409(anon_client: AsyncClient) -> None:
    await anon_client.post("/auth/register", json=TEST_USER)
    resp = await anon_client.post("/auth/register", json=TEST_USER)
    assert resp.status_code == 409


async def test_login(anon_client: AsyncClient) -> None:
    await anon_client.post("/auth/register", json=TEST_USER)
    resp = await anon_client.post(
        "/auth/token",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(anon_client: AsyncClient) -> None:
    await anon_client.post("/auth/register", json=TEST_USER)
    resp = await anon_client.post(
        "/auth/token",
        data={"username": TEST_USER["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_login_unknown_email_returns_401(anon_client: AsyncClient) -> None:
    resp = await anon_client.post(
        "/auth/token",
        data={"username": "nobody@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


async def test_get_me(client: AsyncClient) -> None:
    resp = await client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == TEST_USER["email"]


async def test_get_me_unauthenticated(anon_client: AsyncClient) -> None:
    resp = await anon_client.get("/auth/me")
    assert resp.status_code == 401


async def test_refresh_token(anon_client: AsyncClient) -> None:
    await anon_client.post("/auth/register", json=TEST_USER)
    login_resp = await anon_client.post(
        "/auth/token",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await anon_client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_refresh_invalid_token_returns_401(anon_client: AsyncClient) -> None:
    resp = await anon_client.post(
        "/auth/refresh", json={"refresh_token": "notavalidtoken"}
    )
    assert resp.status_code == 401


async def test_logout(anon_client: AsyncClient) -> None:
    await anon_client.post("/auth/register", json=TEST_USER)
    login_resp = await anon_client.post(
        "/auth/token",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await anon_client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert resp.status_code == 204

    # token should now be revoked
    resp = await anon_client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert resp.status_code == 401
