from datetime import datetime, timezone
from decimal import Decimal

import pytest
from asyncpg import create_pool
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis

from config import get_settings
from main import app
from models import AthreaSeries, ChapterFeed, Manga


settings = get_settings()
TEST_DATABASE_URL = str(settings.database_url).replace("/inkdrop?", "/inkdrop_test?")
TEST_REDIS_URL = str(settings.redis_url).removesuffix("/0") + "/1"
assert "inkdrop_test" in TEST_DATABASE_URL
assert TEST_REDIS_URL.endswith("/1")


class FakeMangadexClient:
    def __init__(self):
        self.latest_free_chapter = "10"
        self.search_results = []

    async def search(self, query: str):
        return self.search_results

    async def get_manga(self, source_id: str) -> Manga:
        return Manga.model_validate(
            {
                "id": source_id,
                "attributes": {
                    "title": {"en": "Possessing My Venus"},
                    "altTitles": [],
                    "description": {"en": "A description"},
                    "status": "ongoing",
                },
                "relationships": [],
            }
        )

    async def get_chapters(self, source_id: str) -> ChapterFeed:
        return ChapterFeed.model_validate(
            {
                "data": [
                    {
                        "id": "chapter-id",
                        "attributes": {
                            "chapter": self.latest_free_chapter,
                            "title": None,
                            "externalUrl": None,
                            "readableAt": "2026-11-20T00:00:00+00:00",
                        },
                    }
                ],
                "limit": 100,
                "offset": 0,
                "total": 1,
            }
        )


class FakeAthreaClient:
    def __init__(self):
        self.latest_free_chapter = Decimal("31")
        self.search_results = []

    async def search(self, query: str):
        return self.search_results

    async def get_series(self, slug: str) -> AthreaSeries:
        return AthreaSeries(
            name="Possessing My Venus",
            cover_url="https://athreascans.com/cover.png",
            status="Ongoing",
            description="A description",
            latest_free_chapter=self.latest_free_chapter,
            latest_free_chapter_datetime=datetime(2026, 9, 27, tzinfo=timezone.utc),
            latest_paid_chapter=Decimal("35"),
        )


@pytest.fixture
async def pool():
    pool = await create_pool(dsn=TEST_DATABASE_URL)
    async with pool.acquire() as conn:
        await conn.execute(
            """
            TRUNCATE users, titles, title_sources, subscriptions, notifications
            RESTART IDENTITY CASCADE
            """
        )
    yield pool
    await pool.close()


@pytest.fixture
async def redis():
    redis = Redis.from_url(url=TEST_REDIS_URL, decode_responses=True)
    await redis.flushdb()
    yield redis
    await redis.aclose()


@pytest.fixture
def mangadex_client():
    return FakeMangadexClient()


@pytest.fixture
def athrea_client():
    return FakeAthreaClient()


@pytest.fixture
async def user_row_id(pool):
    async with pool.acquire() as conn:
        return await conn.fetchval(
            """
            INSERT INTO users (first_name, last_name, email, password_hash)
            VALUES ('Test', 'User', 'test@example.com', 'not-a-real-hash')
            RETURNING row_id
            """
        )


@pytest.fixture
async def client(pool, redis, mangadex_client, athrea_client):
    app.state.pool = pool
    app.state.redis = redis
    app.state.mangadex_client = mangadex_client
    app.state.athrea_client = athrea_client
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://test"
    ) as client:
        yield client
