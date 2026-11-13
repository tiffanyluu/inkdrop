from decimal import Decimal
from typing import Literal
from uuid import UUID

import asyncpg
from db import titles_db
from clients import MangadexClient


async def add_title(
    conn: asyncpg.Connection,
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

    latest_chapter = chapters.latest_free_chapter

    latest_free_chapter = None
    latest_free_chapter_datetime = None
    if latest_chapter is not None and latest_chapter.attributes.chapter is not None:
        latest_free_chapter = Decimal(latest_chapter.attributes.chapter)
        latest_free_chapter_datetime = latest_chapter.attributes.readable_at

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
    except asyncpg.UniqueViolationError:
        return await titles_db.get_title_by_source(conn, source_type, source_id)

    return title_public_id
