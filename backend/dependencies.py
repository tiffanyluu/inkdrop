from typing import Annotated
from asyncpg import Pool, Record
from fastapi import Cookie, Depends, HTTPException, Request
from redis.asyncio import Redis
import utils
from clients import MangadexClient
from db import sessions_db, users_db


async def get_db_pool(request: Request) -> Pool:
    return request.app.state.pool


DbPool = Annotated[Pool, Depends(get_db_pool)]


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis


RedisClient = Annotated[Redis, Depends(get_redis)]


async def get_mangadex_client(request: Request) -> MangadexClient:
    return request.app.state.mangadex_client


async def get_current_user(
    pool: DbPool,
    redis: RedisClient,
    session: Annotated[str | None, Cookie()] = None,
) -> Record:
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    hashed_token = utils.hash_token(session)

    user_row_id = await sessions_db.get_user_row_id(redis, hashed_token)
    if user_row_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    async with pool.acquire() as conn:
        user = await users_db.get_user_by_user_row_id(conn, user_row_id)

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


CurrentUser = Annotated[Record, Depends(get_current_user)]
