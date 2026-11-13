from fastapi import Depends, FastAPI, Request
from config import get_settings
from contextlib import asynccontextmanager
from clients import MangadexClient
from dependencies import get_db_pool
from routes import titles_routes
import asyncpg


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.pool = await asyncpg.create_pool(dsn=str(settings.database_url))
    app.state.mangadex_client = MangadexClient()
    yield
    await app.state.mangadex_client.close()
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)

app.include_router(titles_routes.router)


@app.get("/health")
async def get_health(pool: asyncpg.Pool = Depends(get_db_pool)):
    return await pool.fetchval("SELECT 1")
