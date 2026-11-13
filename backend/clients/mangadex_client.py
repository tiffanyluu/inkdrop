from httpx import TimeoutException, HTTPStatusError, RequestError, AsyncClient, Timeout
import asyncio
from fastapi import HTTPException
from models.mangadex_model import Manga, ChapterFeed


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
        except TimeoutException:
            raise HTTPException(status_code=504, detail="MangaDex API timed out")
        except HTTPStatusError as exc:
            request_id = exc.response.headers.get("X-Request-ID", "N/A")
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"MangaDex error (Request ID: {request_id}): {exc.response.text}",
            )
        except RequestError:
            raise HTTPException(status_code=502, detail="Unable to reach MangaDex")

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
