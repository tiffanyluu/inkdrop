from typing import Annotated

from asyncpg import Pool, Record
from fastapi import Cookie, Depends, HTTPException, Request

import utils
from clients import MangadexClient
from db import sessions_db


async def get_db_pool(request: Request) -> Pool:
    return request.app.state.pool


DbPool = Annotated[Pool, Depends(get_db_pool)]


async def get_mangadex_client(request: Request) -> MangadexClient:
    return request.app.state.mangadex_client


async def get_current_user(
    pool: DbPool,
    session: Annotated[str | None, Cookie()] = None,
) -> Record:
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    hashed_token = utils.hash_token(session)

    async with pool.acquire() as conn:
        user = await sessions_db.get_user_by_token_hash(conn, hashed_token)

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
