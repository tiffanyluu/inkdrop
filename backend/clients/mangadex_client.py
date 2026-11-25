import asyncio

from httpx import AsyncClient, HTTPStatusError, RequestError, Timeout, TimeoutException

from exceptions import MangadexError, MangadexNotFoundError
from models import ChapterFeed, Manga, StandardizedSource


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
            raise MangadexError("MangaDex API timed out")
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                raise MangadexNotFoundError(f"Not found on MangaDex: {path}")
            request_id = e.response.headers.get("X-Request-ID", "N/A")
            raise MangadexError(
                f"MangaDex error {e.response.status_code} (Request ID: {request_id})"
            )
        except RequestError:
            raise MangadexError("Unable to reach MangaDex")

    async def search(self, query: str) -> list[StandardizedSource]:
        response = await self._get(
            "/manga", params={"title": query, "includes[]": "cover_art"}
        )
        search_results = []
        for data in response["data"]:
            manga = Manga.model_validate(data)
            search_results.append(
                StandardizedSource(
                    name=manga.attributes.display_title,
                    cover_url=manga.cover_url,
                    source_id=manga.id,
                    source_type="MANGADEX",
                )
            )
        return search_results

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
