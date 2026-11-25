from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from clients import AthreaClient, MangadexClient
from controllers import titles_controller
from dependencies import get_athrea_client, get_current_user, get_mangadex_client
from exceptions import AthreaError, MangadexError
from models import TitleSource

router = APIRouter(prefix="/titles", dependencies=[Depends(get_current_user)])


class TitleSearchResult(BaseModel):
    name: str
    cover_url: str | None
    sources: list[TitleSource]


@router.get("/search")
async def search_titles(
    query: str,
    mangadex_client: Annotated[MangadexClient, Depends(get_mangadex_client)],
    athrea_client: Annotated[AthreaClient, Depends(get_athrea_client)],
) -> list[TitleSearchResult]:
    try:
        grouped_results = await titles_controller.search_titles(
            mangadex_client, athrea_client, query
        )
    except (MangadexError, AthreaError) as e:
        raise HTTPException(status_code=502, detail=str(e))

    search_results = []
    for results in grouped_results:
        sources = []
        for result in results:
            sources.append(
                TitleSource(
                    source_id=result.source_id, source_type=result.source_type
                )
            )
        search_results.append(
            TitleSearchResult(
                name=results[0].name,
                cover_url=results[0].cover_url,
                sources=sources,
            )
        )
    return search_results
