from datetime import datetime, timezone
from decimal import Decimal

from clients import AthreaClient


async def test_search():
    client = AthreaClient()

    async def fake_get(path, params=None):
        return open("tests/html/athrea_search.html").read()

    client._get = fake_get
    search_results = await client.search("venus")
    await client.close()

    assert len(search_results) == 1
    assert search_results[0].name == "Possessing My Venus"
    assert search_results[0].source_id == "possessing-my-venus"
    assert search_results[0].source_type == "ATHREA"


async def test_get_series():
    client = AthreaClient()

    async def fake_get(path, params=None):
        return open("tests/html/athrea_series.html").read()

    client._get = fake_get
    series = await client.get_series("possessing-my-venus")
    await client.close()

    assert series.name == "Possessing My Venus"
    assert series.status == "Ongoing"
    assert series.latest_free_chapter == Decimal("31")
    assert series.latest_free_chapter_datetime == datetime(
        2026, 9, 27, tzinfo=timezone.utc
    )
    assert series.latest_paid_chapter == Decimal("35")
