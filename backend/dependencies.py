import asyncpg
from fastapi import Request
from clients import MangadexClient


async def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.pool


async def get_mangadex_client(request: Request) -> MangadexClient:
    return request.app.state.mangadex_client
