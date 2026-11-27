from decimal import Decimal

from controllers import subscriptions_controller, titles_controller
from models import StandardizedSource, TitleSource

MANGADEX_SOURCE = TitleSource(source_id="mangadex-id", source_type="MANGADEX")
ATHREA_SOURCE = TitleSource(source_id="possessing-my-venus", source_type="ATHREA")


async def count_notifications(pool, user_row_id):
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM notifications WHERE user_row_id = $1", user_row_id
        )


async def test_sync_new_chapter_creates_notification(
    pool, mangadex_client, athrea_client, user_row_id
):
    await subscriptions_controller.add_subscription(
        pool, mangadex_client, athrea_client, user_row_id, [MANGADEX_SOURCE]
    )

    mangadex_client.latest_free_chapter = "11"
    await titles_controller.sync_chapters(
        pool, mangadex_client, athrea_client, "mangadex-id", "MANGADEX"
    )

    assert await count_notifications(pool, user_row_id) == 1


async def test_sync_no_new_chapter_creates_no_notification(
    pool, mangadex_client, athrea_client, user_row_id
):
    await subscriptions_controller.add_subscription(
        pool, mangadex_client, athrea_client, user_row_id, [MANGADEX_SOURCE]
    )

    await titles_controller.sync_chapters(
        pool, mangadex_client, athrea_client, "mangadex-id", "MANGADEX"
    )

    assert await count_notifications(pool, user_row_id) == 0


async def test_sync_twice_creates_no_duplicate(
    pool, mangadex_client, athrea_client, user_row_id
):
    await subscriptions_controller.add_subscription(
        pool, mangadex_client, athrea_client, user_row_id, [MANGADEX_SOURCE]
    )

    mangadex_client.latest_free_chapter = "11"
    await titles_controller.sync_chapters(
        pool, mangadex_client, athrea_client, "mangadex-id", "MANGADEX"
    )
    await titles_controller.sync_chapters(
        pool, mangadex_client, athrea_client, "mangadex-id", "MANGADEX"
    )

    assert await count_notifications(pool, user_row_id) == 1


async def test_sync_site_behind_creates_no_notification(
    pool, mangadex_client, athrea_client, user_row_id
):
    await subscriptions_controller.add_subscription(
        pool,
        mangadex_client,
        athrea_client,
        user_row_id,
        [MANGADEX_SOURCE, ATHREA_SOURCE],
    )

    mangadex_client.latest_free_chapter = "11"
    await titles_controller.sync_chapters(
        pool, mangadex_client, athrea_client, "mangadex-id", "MANGADEX"
    )
    assert await count_notifications(pool, user_row_id) == 0

    athrea_client.latest_free_chapter = Decimal("32")
    await titles_controller.sync_chapters(
        pool, mangadex_client, athrea_client, "possessing-my-venus", "ATHREA"
    )
    assert await count_notifications(pool, user_row_id) == 1


async def test_add_title_two_sources_creates_one_title(
    pool, mangadex_client, athrea_client
):
    await titles_controller.add_title(
        pool, mangadex_client, athrea_client, [MANGADEX_SOURCE, ATHREA_SOURCE]
    )

    async with pool.acquire() as conn:
        assert await conn.fetchval("SELECT COUNT(*) FROM titles") == 1
        assert await conn.fetchval("SELECT COUNT(*) FROM title_sources") == 2


async def test_add_title_existing_source_reuses_title(
    pool, mangadex_client, athrea_client
):
    first_title_row_id = await titles_controller.add_title(
        pool, mangadex_client, athrea_client, [MANGADEX_SOURCE]
    )
    second_title_row_id = await titles_controller.add_title(
        pool, mangadex_client, athrea_client, [MANGADEX_SOURCE, ATHREA_SOURCE]
    )

    assert first_title_row_id == second_title_row_id
    async with pool.acquire() as conn:
        assert await conn.fetchval("SELECT COUNT(*) FROM titles") == 1
        assert await conn.fetchval("SELECT COUNT(*) FROM title_sources") == 2


async def test_add_subscription_twice_returns_same_subscription(
    pool, mangadex_client, athrea_client, user_row_id
):
    first_subscription_public_id = await subscriptions_controller.add_subscription(
        pool, mangadex_client, athrea_client, user_row_id, [MANGADEX_SOURCE]
    )
    second_subscription_public_id = await subscriptions_controller.add_subscription(
        pool, mangadex_client, athrea_client, user_row_id, [MANGADEX_SOURCE]
    )

    assert first_subscription_public_id == second_subscription_public_id


async def test_search_merges_same_name_and_author(mangadex_client, athrea_client):
    mangadex_client.search_results = [
        StandardizedSource(
            name="Possessing My Venus",
            cover_url=None,
            authors=["Venus Author (金星)"],
            source_id="mangadex-id",
            source_type="MANGADEX",
        ),
        StandardizedSource(
            name="Some Other Series",
            cover_url=None,
            authors=["Someone Else"],
            source_id="other-id",
            source_type="MANGADEX",
        ),
    ]
    athrea_client.search_results = [
        StandardizedSource(
            name="Possessing my Venus!",
            cover_url=None,
            source_id="possessing-my-venus",
            source_type="ATHREA",
        ),
    ]

    grouped_results = await titles_controller.search_titles(
        mangadex_client, athrea_client, "venus"
    )

    assert len(grouped_results) == 2
    assert len(grouped_results[0]) == 2
    assert len(grouped_results[1]) == 1


async def test_search_does_not_merge_same_name_different_author(
    mangadex_client, athrea_client
):
    mangadex_client.search_results = [
        StandardizedSource(
            name="Possessing My Venus",
            cover_url=None,
            authors=["Different Author"],
            source_id="mangadex-id",
            source_type="MANGADEX",
        ),
    ]
    athrea_client.search_results = [
        StandardizedSource(
            name="Possessing My Venus",
            cover_url=None,
            source_id="possessing-my-venus",
            source_type="ATHREA",
        ),
    ]

    grouped_results = await titles_controller.search_titles(
        mangadex_client, athrea_client, "venus"
    )

    assert len(grouped_results) == 2
    assert len(grouped_results[0]) == 1
    assert len(grouped_results[1]) == 1


async def test_search_does_not_merge_two_mangadex_results_with_same_name(
    mangadex_client, athrea_client
):
    mangadex_client.search_results = [
        StandardizedSource(
            name="Possessing My Venus",
            cover_url=None,
            authors=["Venus Author"],
            source_id="mangadex-id",
            source_type="MANGADEX",
        ),
        StandardizedSource(
            name="Possessing My Venus",
            cover_url=None,
            authors=["Venus Author"],
            source_id="other-mangadex-id",
            source_type="MANGADEX",
        ),
    ]

    grouped_results = await titles_controller.search_titles(
        mangadex_client, athrea_client, "venus"
    )

    assert len(grouped_results) == 2
