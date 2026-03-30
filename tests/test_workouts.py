from httpx import AsyncClient

WORKOUT_PAYLOAD = {"name": "Monday Push", "notes": "Felt good"}


async def test_create_workout(client: AsyncClient) -> None:
    resp = await client.post("/workouts", json=WORKOUT_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Monday Push"
    assert data["notes"] == "Felt good"
    assert "id" in data
    assert "workout_date" in data


async def test_create_workout_unauthenticated(anon_client: AsyncClient) -> None:
    resp = await anon_client.post("/workouts", json=WORKOUT_PAYLOAD)
    assert resp.status_code == 401


async def test_list_workouts(client: AsyncClient) -> None:
    await client.post("/workouts", json={"name": "Workout A"})
    await client.post("/workouts", json={"name": "Workout B"})

    resp = await client.get("/workouts")
    assert resp.status_code == 200
    names = [w["name"] for w in resp.json()]
    assert "Workout A" in names
    assert "Workout B" in names


async def test_list_workouts_sets_total_count_header(client: AsyncClient) -> None:
    await client.post("/workouts", json={"name": "W1"})
    await client.post("/workouts", json={"name": "W2"})

    resp = await client.get("/workouts")
    assert resp.status_code == 200
    assert "x-total-count" in resp.headers
    assert int(resp.headers["x-total-count"]) == 2


async def test_get_workout(client: AsyncClient) -> None:
    created = (await client.post("/workouts", json=WORKOUT_PAYLOAD)).json()
    resp = await client.get(f"/workouts/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Monday Push"


async def test_get_workout_not_found(client: AsyncClient) -> None:
    resp = await client.get("/workouts/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_update_workout(client: AsyncClient) -> None:
    created = (await client.post("/workouts", json=WORKOUT_PAYLOAD)).json()
    resp = await client.patch(
        f"/workouts/{created['id']}", json={"name": "Updated Name", "notes": None}
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"


async def test_delete_workout(client: AsyncClient) -> None:
    created = (await client.post("/workouts", json=WORKOUT_PAYLOAD)).json()
    resp = await client.delete(f"/workouts/{created['id']}")
    assert resp.status_code == 204

    resp = await client.get(f"/workouts/{created['id']}")
    assert resp.status_code == 404


async def test_delete_workout_not_found(client: AsyncClient) -> None:
    resp = await client.delete("/workouts/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_workout_name_is_optional(client: AsyncClient) -> None:
    resp = await client.post("/workouts", json={})
    assert resp.status_code == 201
    assert resp.json()["name"] is None


async def test_create_workout_with_date(client: AsyncClient) -> None:
    resp = await client.post("/workouts", json={"workout_date": "2024-01-15"})
    assert resp.status_code == 201
    assert resp.json()["workout_date"] == "2024-01-15"


async def test_list_workouts_search(client: AsyncClient) -> None:
    await client.post("/workouts", json={"name": "Push Day"})
    await client.post("/workouts", json={"name": "Pull Day"})

    resp = await client.get("/workouts?search=Push")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["name"] == "Push Day"


async def test_set_counts_per_workout_empty(client: AsyncClient) -> None:
    resp = await client.get("/workouts/setcounts")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_workout_streak_empty(client: AsyncClient) -> None:
    resp = await client.get("/workouts/streak")
    assert resp.status_code == 200
    assert resp.json() == 0
