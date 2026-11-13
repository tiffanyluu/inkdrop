from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from asyncpg import UniqueViolationError, Connection
from models.mangadex_model import ChapterFeed
from db import titles_db
from clients import MangadexClient
from exceptions import SourceNotFoundError


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


async def add_title(
    conn: Connection,
    client: MangadexClient,
    source_type: Literal["MANGADEX", "ATHREA"],
    source_id: str,
) -> UUID:
    title_public_id = await titles_db.get_title_by_source(conn, source_type, source_id)
    if title_public_id is not None:
        return title_public_id

    manga = await client.get_manga(source_id)
    chapters = await client.get_chapters(source_id)

    manga_status = (
        manga.attributes.status.upper()
        if manga.attributes.status != "cancelled"
        else "CANCELED"
    )

    [latest_free_chapter, latest_free_chapter_datetime] = (
        get_latest_available_chapter_info(chapters)
    )

    try:
        async with conn.transaction():
            [title_row_id, title_public_id] = await titles_db.create_title(
                conn,
                manga.attributes.display_title,
                manga_status,
                manga.cover_url,
                manga.attributes.display_description,
            )

            await titles_db.create_title_source(
                conn,
                title_id=title_row_id,
                source_type=source_type,
                source_id=source_id,
                latest_free_chapter=latest_free_chapter,
                latest_free_chapter_datetime=latest_free_chapter_datetime,
            )
    except UniqueViolationError:
        return await titles_db.get_title_by_source(conn, source_type, source_id)

    return title_public_id


async def refresh_title_source(
    conn: Connection,
    client: MangadexClient,
    source_id: str,
    source_type: Literal["MANGADEX", "ATHREA"],
) -> None:
    row = await titles_db.get_source_by_source_id_type(conn, source_id, source_type)

    if row is None:
        raise SourceNotFoundError(
            f"No source found with source id {source_id} and source type {source_type}"
        )

    stored_latest_free_chapter = row["latest_free_chapter"]

    chapters = await client.get_chapters(source_id)

    [latest_free_chapter, latest_free_chapter_datetime] = (
        get_latest_available_chapter_info(chapters)
    )

    has_new_chapter = latest_free_chapter is not None and (
        stored_latest_free_chapter is None
        or latest_free_chapter > stored_latest_free_chapter
    )

    if has_new_chapter:
        await titles_db.update_latest_chapter(
            conn=conn,
            source_id=source_id,
            source_type=source_type,
            latest_free_chapter=latest_free_chapter,
            latest_free_chapter_datetime=latest_free_chapter_datetime,
        )

    await titles_db.update_last_checked_datetime(conn, source_id, source_type)
