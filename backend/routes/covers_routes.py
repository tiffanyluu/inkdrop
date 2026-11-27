from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from urllib.parse import urlparse
from clients import CoversClient
from dependencies import get_covers_client
from exceptions import CoverError, CoverNotFoundError

router = APIRouter(prefix="/covers")


@router.get("")
async def get_cover_images(
    url: str, covers_client: Annotated[CoversClient, Depends(get_covers_client)]
) -> Response:
    if urlparse(url).hostname not in ["uploads.mangadex.org", "athreascans.com"]:
        raise HTTPException(status_code=400, detail="Invalid request")

    try:
        cover = await covers_client.get_cover(url)
        return Response(
            content=cover.image_bytes,
            media_type=cover.content_type,
            headers={"Cache-Control": "public, max-age=604800"},
        )
    except CoverNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CoverError as e:
        raise HTTPException(status_code=502, detail=str(e))
