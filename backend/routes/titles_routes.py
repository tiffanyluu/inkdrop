from typing import Literal
from uuid import UUID

from asyncpg import Pool
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from controllers.titles_controller import add_title, refresh_title_source
from dependencies import get_db_pool, get_mangadex_client
from clients import MangadexClient
from exceptions import SourceNotFoundError

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
    pool: Pool = Depends(get_db_pool),
):
    if title.source_type != "MANGADEX":
        raise HTTPException(status_code=400, detail="not supported yet")
    async with pool.acquire() as conn:
        title_id = await add_title(conn, client, title.source_type, title.source_id)
        return TitleResponse(id=title_id)


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh_title(
    title: TitleRequest,
    client: MangadexClient = Depends(get_mangadex_client),
    pool: Pool = Depends(get_db_pool),
):
    if title.source_type != "MANGADEX":
        raise HTTPException(status_code=400, detail="not supported yet")
    try:
        async with pool.acquire() as conn:
            await refresh_title_source(conn, client, title.source_id, title.source_type)
    except SourceNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
