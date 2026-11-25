from datetime import datetime
from decimal import Decimal

from httpx import AsyncClient, HTTPStatusError, RequestError, Timeout, TimeoutException
from bs4 import BeautifulSoup

from models import StandardizedSource, AthreaSeries
from exceptions import AthreaError, AthreaNotFoundError


class AthreaClient:
    def __init__(self):
        self.client = AsyncClient(
            base_url="https://athreascans.com",
            headers={
                "Accept": "text/html",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
            },
            timeout=Timeout(10.0, connect=3.0),
        )

    async def close(self):
        await self.client.aclose()

    async def _get(self, path: str, params: dict | None = None) -> str:
        try:
            response = await self.client.get(path, params=params)
            response.raise_for_status()
            return response.text
        except TimeoutException:
            raise AthreaError("Athrea timed out")
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                raise AthreaNotFoundError(f"Not found on Athrea: {path}")
            raise AthreaError(f"Athrea error {e.response.status_code}")
        except RequestError:
            raise AthreaError("Unable to reach Athrea")

    async def search(self, query: str) -> list[StandardizedSource]:
        html = await self._get("/", params={"s": query})
        soup = BeautifulSoup(html, "html.parser")
        search_results = []
        for a in soup.select("div.bsx > a"):
            search_results.append(
                StandardizedSource(
                    name=a["title"],
                    cover_url=a.select_one("img")["src"],
                    source_id=a["href"].rstrip("/").split("/")[-1],
                    source_type="ATHREA",
                )
            )
        return search_results

    async def get_series(self, slug: str) -> AthreaSeries:
        html = await self._get(f"/manga/{slug}/")
        soup = BeautifulSoup(html, "html.parser")

        status = None
        for row in soup.select("table.infotable tr"):
            cells = row.select("td")
            if cells[0].text.strip() == "Status":
                status = cells[1].text.strip()

        latest_free_chapter = None
        latest_free_chapter_date = None
        latest_paid_chapter = None
        for li in soup.select("#chapterlist li"):
            if li.select_one("a").has_attr("href"):
                latest_free_chapter = Decimal(li["data-num"])
                latest_free_chapter_date = datetime.strptime(
                    li.select_one("span.chapterdate").text.strip(), "%B %d, %Y"
                ).date()
                break
            if latest_paid_chapter is None:
                latest_paid_chapter = Decimal(li["data-num"])

        return AthreaSeries(
            name=soup.select_one("h1.entry-title").text.strip(),
            cover_url=soup.select_one("div.thumb img")["src"],
            status=status,
            description=soup.select_one("div.entry-content").text.strip(),
            latest_free_chapter=latest_free_chapter,
            latest_free_chapter_date=latest_free_chapter_date,
            latest_paid_chapter=latest_paid_chapter,
        )
