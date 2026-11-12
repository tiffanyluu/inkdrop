from fastapi import Depends, FastAPI, Request
from config import get_settings
from contextlib import asynccontextmanager
import asyncpg


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.pool = await asyncpg.create_pool(dsn=str(settings.database_url))
    yield
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)


async def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.pool


@app.get("/health")
async def get_health(pool: asyncpg.Pool = Depends(get_db_pool)):
    return await pool.fetchval("SELECT 1")
