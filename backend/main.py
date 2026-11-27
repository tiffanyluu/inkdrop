from contextlib import asynccontextmanager

from asyncpg import create_pool
from fastapi import FastAPI

from clients import AthreaClient, MangadexClient, CoversClient
from config import get_settings
from dependencies import DbPool
from routes import (
    auth_routes,
    subscriptions_routes,
    titles_routes,
    notifications_routes,
    covers_routes,
)

from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.pool = await create_pool(dsn=str(settings.database_url))
    app.state.redis = Redis.from_url(url=str(settings.redis_url), decode_responses=True)
    await app.state.redis.ping()
    app.state.mangadex_client = MangadexClient()
    app.state.athrea_client = AthreaClient()
    app.state.covers_client = CoversClient()
    yield
    await app.state.covers_client.close()
    await app.state.athrea_client.close()
    await app.state.mangadex_client.close()
    await app.state.redis.aclose()
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)

app.include_router(titles_routes.router)
app.include_router(auth_routes.router)
app.include_router(subscriptions_routes.router)
app.include_router(notifications_routes.router)
app.include_router(covers_routes.router)


@app.get("/health")
async def get_health(
    pool: DbPool,
):
    return await pool.fetchval("SELECT 1")
