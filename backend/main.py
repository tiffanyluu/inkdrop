from contextlib import asynccontextmanager

from asyncpg import create_pool
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from clients import MangadexClient
from config import get_settings
from dependencies import DbPool
from exceptions import MangadexError, MangadexNotFoundError, MangadexTimeoutError
from routes import auth_routes, titles_routes


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


@app.exception_handler(MangadexError)
async def handle_mangadex_error(_request: Request, e: MangadexError) -> JSONResponse:
    if isinstance(e, MangadexNotFoundError):
        status_code = 404
    elif isinstance(e, MangadexTimeoutError):
        status_code = 504
    else:
        status_code = 502
    return JSONResponse(status_code=status_code, content={"detail": str(e)})


@app.get("/health")
async def get_health(
    pool: DbPool,
):
    return await pool.fetchval("SELECT 1")
