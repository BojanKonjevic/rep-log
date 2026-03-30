from httpx import ASGITransport, AsyncClient

from rep_log.seed import DEFAULT_EXERCISES

# Names guaranteed not to exist in the seeded defaults
UNIQUE_NAME = "Goblet Squat"
UNIQUE_NAME_2 = "Cable Fly"
UNIQUE_NAME_3 = "Landmine Press"

# A name that IS in the defaults — useful for 409 tests
SEEDED_NAME = next(iter(DEFAULT_EXERCISES))  # e.g. "Bench Press"


async def test_create_exercise(client: AsyncClient) -> None:
    resp = await client.post("/exercises", json={"name": UNIQUE_NAME})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == UNIQUE_NAME
    assert "id" in data


async def test_create_exercise_unauthenticated(anon_client: AsyncClient) -> None:
    resp = await anon_client.post("/exercises", json={"name": UNIQUE_NAME})
    assert resp.status_code == 401


async def test_list_exercises_returns_defaults(client: AsyncClient) -> None:
    """Registration seeds default exercises, so the list is non-empty from the start."""
    resp = await client.get("/exercises")
    assert resp.status_code == 200
    names = {e["name"] for e in resp.json()}
    assert SEEDED_NAME in names


async def test_get_exercise(client: AsyncClient) -> None:
    created = (await client.post("/exercises", json={"name": UNIQUE_NAME})).json()
    resp = await client.get(f"/exercises/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == UNIQUE_NAME


async def test_get_exercise_not_found(client: AsyncClient) -> None:
    resp = await client.get("/exercises/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_update_exercise(client: AsyncClient) -> None:
    created = (await client.post("/exercises", json={"name": UNIQUE_NAME})).json()
    resp = await client.patch(
        f"/exercises/{created['id']}", json={"name": UNIQUE_NAME_2}
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == UNIQUE_NAME_2


async def test_update_exercise_not_found(client: AsyncClient) -> None:
    resp = await client.patch(
        "/exercises/00000000-0000-0000-0000-000000000000", json={"name": "Anything"}
    )
    assert resp.status_code == 404


async def test_delete_exercise(client: AsyncClient) -> None:
    created = (await client.post("/exercises", json={"name": UNIQUE_NAME})).json()
    resp = await client.delete(f"/exercises/{created['id']}")
    assert resp.status_code == 204

    resp = await client.get(f"/exercises/{created['id']}")
    assert resp.status_code == 404


async def test_delete_exercise_not_found(client: AsyncClient) -> None:
    resp = await client.delete("/exercises/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_duplicate_exercise_returns_409(client: AsyncClient) -> None:
    """The seeded defaults already include SEEDED_NAME — creating it again is a 409."""
    resp = await client.post("/exercises", json={"name": SEEDED_NAME})
    assert resp.status_code == 409


async def test_create_exercise_with_unknown_muscle_group_returns_422(
    client: AsyncClient,
) -> None:
    resp = await client.post(
        "/exercises",
        json={"name": UNIQUE_NAME, "muscle_group_names": ["does_not_exist"]},
    )
    assert resp.status_code == 422


async def test_list_exercises_limit_respected(client: AsyncClient) -> None:
    """32 defaults are seeded; limit=5 must return exactly 5."""
    resp = await client.get("/exercises?limit=5")
    assert resp.status_code == 200
    assert len(resp.json()) == 5


async def test_list_exercises_page_2(client: AsyncClient) -> None:
    """With 32 defaults and limit=10, page 4 returns 2 items."""
    resp = await client.get("/exercises?page=4&limit=10")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_exercises_isolated_per_user(
    session: object,
) -> None:
    """An exercise created by user A is not visible to user B."""
    from rep_log.database import get_session
    from rep_log.main import app

    async def override() -> object:  # type: ignore[misc]
        yield session

    app.dependency_overrides[get_session] = override

    async def make_client(email: str, password: str) -> AsyncClient:
        ac = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        await ac.__aenter__()
        await ac.post("/auth/register", json={"email": email, "password": password})
        tok = (
            await ac.post("/auth/token", data={"username": email, "password": password})
        ).json()["access_token"]
        ac.headers["Authorization"] = f"Bearer {tok}"
        return ac

    client_a = await make_client("a_iso@example.com", "pass1234!!")
    client_b = await make_client("b_iso@example.com", "pass1234!!")

    try:
        await client_a.post("/exercises", json={"name": "Secret Exercise XYZ"})
        resp = await client_b.get("/exercises?limit=100")
        names = {e["name"] for e in resp.json()}
        assert "Secret Exercise XYZ" not in names
    finally:
        await client_a.__aexit__(None, None, None)
        await client_b.__aexit__(None, None, None)
        app.dependency_overrides.clear()
