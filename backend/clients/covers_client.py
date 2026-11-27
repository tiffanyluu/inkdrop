from httpx import AsyncClient, HTTPStatusError, RequestError, Timeout, TimeoutException

from exceptions import CoverError, CoverNotFoundError
from models import CoverResult


class CoversClient:
    def __init__(self):
        self.client = AsyncClient(
            headers={
                "Accept": "image/*",
            },
            timeout=Timeout(10.0, connect=3.0),
        )

    async def close(self):
        await self.client.aclose()

    async def get_cover(self, url: str) -> CoverResult:
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return CoverResult(
                image_bytes=response.content,
                content_type=response.headers["content-type"],
            )
        except TimeoutException:
            raise CoverError("Cover timed out")
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                raise CoverNotFoundError(f"Cover not found: {url}")
            raise CoverError(f"Cover error {e.response.status_code}")
        except RequestError:
            raise CoverError("Unable to reach cover")
