from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from clients import MangadexClient
from controllers import titles_controller
from dependencies import DbPool, get_current_user, get_mangadex_client
from exceptions import SourceNotFoundError
from models import SourceType

router = APIRouter(prefix="/titles", dependencies=[Depends(get_current_user)])


class TitleRequest(BaseModel):
    source_id: str
    source_type: SourceType


class TitleResponse(BaseModel):
    title_public_id: UUID


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_title(
    title: TitleRequest,
    client: Annotated[MangadexClient, Depends(get_mangadex_client)],
    pool: DbPool,
) -> TitleResponse:
    if title.source_type != "MANGADEX":
        raise HTTPException(status_code=400, detail="Not supported yet")
    async with pool.acquire() as conn:
        _, title_public_id = await titles_controller.add_title(
            conn,
            client,
            title.source_id,
            title.source_type,
        )
        return TitleResponse(title_public_id=title_public_id)


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh_title(
    title: TitleRequest,
    client: Annotated[MangadexClient, Depends(get_mangadex_client)],
    pool: DbPool,
) -> None:
    if title.source_type != "MANGADEX":
        raise HTTPException(status_code=400, detail="Not supported yet")
    try:
        async with pool.acquire() as conn:
            await titles_controller.refresh_title_source(
                conn, client, title.source_id, title.source_type
            )
    except SourceNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
