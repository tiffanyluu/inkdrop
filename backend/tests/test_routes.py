from httpx import AsyncClient


async def signup_and_login(client: AsyncClient, email: str):
    await client.post(
        "/auth/signup",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "password": "password123",
        },
    )
    await client.post("/auth/login", json={"email": email, "password": "password123"})


async def test_subscriptions_requires_login(client):
    response = await client.get("/subscriptions")

    assert response.status_code == 401


async def test_search_requires_login(client):
    response = await client.get("/titles/search", params={"query": "venus"})

    assert response.status_code == 401


async def test_subscribe(client):
    await signup_and_login(client, "first@example.com")

    response = await client.post(
        "/subscriptions",
        json={"sources": [{"source_id": "mangadex-id", "source_type": "MANGADEX"}]},
    )

    assert response.status_code == 201


async def test_subscribe_with_no_sources(client):
    await signup_and_login(client, "first@example.com")

    response = await client.post("/subscriptions", json={"sources": []})

    assert response.status_code == 422


async def test_cannot_delete_other_users_subscription(client):
    await signup_and_login(client, "first@example.com")
    response = await client.post(
        "/subscriptions",
        json={"sources": [{"source_id": "mangadex-id", "source_type": "MANGADEX"}]},
    )
    subscription_public_id = response.json()["subscription_public_id"]

    client.cookies.clear()
    await signup_and_login(client, "second@example.com")
    response = await client.delete(f"/subscriptions/{subscription_public_id}")

    assert response.status_code == 404
