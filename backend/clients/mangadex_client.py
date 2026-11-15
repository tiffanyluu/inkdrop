import asyncio

from httpx import AsyncClient, HTTPStatusError, RequestError, Timeout, TimeoutException

from exceptions import (
    MangadexError,
    MangadexNotFoundError,
    MangadexTimeoutError,
    MangadexUnavailableError,
)
from models.mangadex_model import ChapterFeed, Manga


class MangadexClient:
    def __init__(self):
        self.client = AsyncClient(
            base_url="https://api.mangadex.org",
            headers={"Accept": "application/json"},
            timeout=Timeout(10.0, connect=3.0),
        )

    async def close(self):
        await self.client.aclose()

    async def _get(self, path: str, params: dict | None = None) -> dict:
        try:
            response = await self.client.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except TimeoutException as e:
            raise MangadexTimeoutError("MangaDex API timed out") from e
        except HTTPStatusError as e:
            status_code = e.response.status_code
            request_id = e.response.headers.get("X-Request-ID", "N/A")
            if status_code == 404:
                raise MangadexNotFoundError(f"Not found on MangaDex: {path}") from e
            raise MangadexError(
                f"MangaDex returned {status_code} (Request ID: {request_id})"
            ) from e
        except RequestError as e:
            raise MangadexUnavailableError("Unable to reach MangaDex") from e

    async def get_manga(self, source_id: str) -> Manga:
        response = await self._get(
            f"/manga/{source_id}", params={"includes[]": "cover_art"}
        )
        manga = Manga.model_validate(response["data"])
        return manga

    async def get_chapters(self, source_id: str) -> ChapterFeed:
        response = await self._get(
            f"/manga/{source_id}/feed",
            params={"translatedLanguage[]": "en", "order[chapter]": "desc"},
        )
        chapters = ChapterFeed.model_validate(response)
        return chapters


if __name__ == "__main__":

    async def test():
        client = MangadexClient()
        try:
            chapter = await client.get_chapters("0184c74d-5c59-45db-83dd-c00456cf6fe3")
            print(chapter.model_dump_json(indent=2))
            # manga = await client.get_manga("0184c74d-5c59-45db-83dd-c00456cf6fe3")
            # print(manga.model_dump_json(indent=2))
        finally:
            await client.close()

    asyncio.run(test())
