from typing import Literal
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from controllers.titles_controller import add_title
from dependencies import get_db_pool, get_mangadex_client
from clients import MangadexClient

router = APIRouter(prefix="/titles")


class TitleRequest(BaseModel):
    source_id: str
    source_type: Literal["MANGADEX", "ATHREA"]


class TitleResponse(BaseModel):
    id: UUID


@router.post("", response_model=TitleResponse, status_code=status.HTTP_201_CREATED)
async def create_title(
    title: TitleRequest,
    client: MangadexClient = Depends(get_mangadex_client),
    pool: asyncpg.Pool = Depends(get_db_pool),
):
    if title.source_type != "MANGADEX":
        raise HTTPException(status_code=400, detail="not supported yet")
    async with pool.acquire() as conn:
        title_id = await add_title(conn, client, title.source_type, title.source_id)
        return TitleResponse(id=title_id)
