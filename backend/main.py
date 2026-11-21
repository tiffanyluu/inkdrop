from contextlib import asynccontextmanager

from asyncpg import create_pool
from fastapi import FastAPI

from clients import MangadexClient
from config import get_settings
from dependencies import DbPool
from routes import (
    auth_routes,
    subscriptions_routes,
    titles_routes,
    notifications_routes,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.pool = await create_pool(dsn=str(settings.database_url))
    app.state.mangadex_client = MangadexClient()
    yield
    await app.state.mangadex_client.close()
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)

app.include_router(titles_routes.router)
app.include_router(auth_routes.router)
app.include_router(subscriptions_routes.router)
app.include_router(notifications_routes.router)


@app.get("/health")
async def get_health(
    pool: DbPool,
):
    return await pool.fetchval("SELECT 1")
