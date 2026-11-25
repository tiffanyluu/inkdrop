import asyncio
from datetime import datetime
from decimal import Decimal

from asyncpg import Pool, UniqueViolationError

from clients import AthreaClient, MangadexClient
from db import titles_db, notifications_db, subscriptions_db
from exceptions import SourceNotFoundError
from models import ChapterFeed, SourceType, StandardizedSource, TitleSource


def get_latest_available_chapter_info(
    chapters: ChapterFeed,
) -> tuple[Decimal | None, datetime | None]:
    latest_chapter = chapters.latest_free_chapter

    latest_free_chapter = None
    latest_free_chapter_datetime = None
    if latest_chapter is not None and latest_chapter.attributes.chapter is not None:
        latest_free_chapter = Decimal(latest_chapter.attributes.chapter)
        latest_free_chapter_datetime = latest_chapter.attributes.readable_at

    return latest_free_chapter, latest_free_chapter_datetime


async def search_titles(
    mangadex_client: MangadexClient,
    athrea_client: AthreaClient,
    query: str,
) -> list[list[StandardizedSource]]:
    mangadex_results, athrea_results = await asyncio.gather(
        mangadex_client.search(query),
        athrea_client.search(query),
    )

    grouped_results = {}
    for result in mangadex_results + athrea_results:
        normalized_name = "".join(c for c in result.name.lower() if c.isalnum())
        if normalized_name not in grouped_results:
            grouped_results[normalized_name] = []
        grouped_results[normalized_name].append(result)

    return list(grouped_results.values())


async def add_title(
    pool: Pool,
    mangadex_client: MangadexClient,
    athrea_client: AthreaClient,
    sources: list[TitleSource],
) -> int:
    title_row_id = None
    new_sources = []
    async with pool.acquire() as conn:
        for source in sources:
            row = await titles_db.get_title_by_source(
                conn, source.source_id, source.source_type
            )
            if row is None:
                new_sources.append(source)
            else:
                title_row_id = row["row_id"]

    for source in new_sources:
        if source.source_type == "MANGADEX":
            manga = await mangadex_client.get_manga(source.source_id)
            chapters = await mangadex_client.get_chapters(source.source_id)
            title_name = manga.attributes.display_title
            title_status = (
                manga.attributes.status.upper()
                if manga.attributes.status != "cancelled"
                else "CANCELED"
            )
            cover_url = manga.cover_url
            description = manga.attributes.display_description
            latest_free_chapter, latest_free_chapter_datetime = (
                get_latest_available_chapter_info(chapters)
            )
        else:
            series = await athrea_client.get_series(source.source_id)
            title_name = series.name
            title_status = series.status.upper()
            cover_url = series.cover_url
            description = series.description
            latest_free_chapter = series.latest_free_chapter
            latest_free_chapter_datetime = series.latest_free_chapter_datetime

        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    if title_row_id is None:
                        title_row_id, _ = await titles_db.create_title(
                            conn, title_name, title_status, cover_url, description
                        )
                    await titles_db.create_title_source(
                        conn,
                        title_row_id,
                        source.source_id,
                        source.source_type,
                        latest_free_chapter,
                        latest_free_chapter_datetime,
                    )
        except UniqueViolationError:
            async with pool.acquire() as conn:
                row = await titles_db.get_title_by_source(
                    conn, source.source_id, source.source_type
                )
            title_row_id = row["row_id"]

    return title_row_id


async def sync_chapters(
    pool: Pool,
    mangadex_client: MangadexClient,
    athrea_client: AthreaClient,
    source_id: str,
    source_type: SourceType,
) -> None:
    async with pool.acquire() as conn:
        title_source = await titles_db.get_source_by_source_id_type(
            conn, source_id, source_type
        )

    if title_source is None:
        raise SourceNotFoundError(
            f"No source found with source id {source_id} and source type {source_type}"
        )

    stored_latest_free_chapter = title_source["latest_free_chapter"]

    if source_type == "MANGADEX":
        chapters = await mangadex_client.get_chapters(source_id)
        latest_free_chapter, latest_free_chapter_datetime = (
            get_latest_available_chapter_info(chapters)
        )
    else:
        series = await athrea_client.get_series(source_id)
        latest_free_chapter = series.latest_free_chapter
        latest_free_chapter_datetime = series.latest_free_chapter_datetime

    has_new_chapter = latest_free_chapter is not None and (
        stored_latest_free_chapter is None
        or latest_free_chapter > stored_latest_free_chapter
    )

    async with pool.acquire() as conn:
        if has_new_chapter:
            async with conn.transaction():
                await titles_db.update_latest_chapter(
                    conn,
                    source_id,
                    source_type,
                    latest_free_chapter,
                    latest_free_chapter_datetime,
                )
                await notifications_db.create_notifications(
                    conn, title_source["title_row_id"], latest_free_chapter
                )
                await subscriptions_db.update_latest_notified_chapter(
                    conn, title_source["title_row_id"], latest_free_chapter
                )

        await titles_db.update_last_checked_datetime(conn, source_id, source_type)
