from datetime import datetime
from decimal import Decimal

from asyncpg import Connection, Record


async def create_title(
    conn: Connection,
    name: str,
    status: str,
    cover_url: str | None,
    description: str | None,
) -> Record:
    return await conn.fetchrow(
        """
        INSERT INTO titles (title_name, cover_url, title_status, description)
        VALUES ($1, $2, $3, $4)
        RETURNING row_id, title_public_id
        """,
        name,
        cover_url,
        status,
        description,
    )


async def create_title_source(
    conn: Connection,
    title_row_id: int,
    source_id: str,
    source_type: str,
    latest_free_chapter: Decimal | None,
    latest_free_chapter_datetime: datetime | None,
) -> None:
    await conn.execute(
        """
        INSERT INTO title_sources (
            title_row_id, source_id, source_type, latest_free_chapter, latest_free_chapter_datetime
        )
        VALUES ($1, $2, $3, $4, $5)
        """,
        title_row_id,
        source_id,
        source_type,
        latest_free_chapter,
        latest_free_chapter_datetime,
    )


async def get_title_by_source(
    conn: Connection,
    source_id: str,
    source_type: str,
) -> Record | None:
    return await conn.fetchrow(
        """
        SELECT t.row_id, t.title_public_id FROM titles t JOIN title_sources ts
        ON t.row_id = ts.title_row_id
        WHERE ts.source_type = $1 AND ts.source_id = $2
        """,
        source_type,
        source_id,
    )


async def get_source_by_source_id_type(
    conn: Connection, source_id: str, source_type: str
) -> Record | None:
    return await conn.fetchrow(
        """
        SELECT ts.title_row_id, ts.latest_free_chapter, ts.latest_free_chapter_datetime
        FROM title_sources ts WHERE ts.source_id = $1 AND ts.source_type = $2
        """,
        source_id,
        source_type,
    )


async def update_latest_chapter(
    conn: Connection,
    source_id: str,
    source_type: str,
    latest_free_chapter: Decimal | None,
    latest_free_chapter_datetime: datetime | None,
) -> None:
    await conn.execute(
        """
        UPDATE title_sources
        SET latest_free_chapter = $1, 
            latest_free_chapter_datetime = $2
        WHERE source_id = $3 AND source_type = $4
        """,
        latest_free_chapter,
        latest_free_chapter_datetime,
        source_id,
        source_type,
    )


async def update_last_checked_datetime(
    conn: Connection, source_id: str, source_type: str
) -> None:
    await conn.execute(
        """
        UPDATE title_sources
        SET last_checked_datetime = now()
        WHERE source_id = $1 AND source_type = $2
        """,
        source_id,
        source_type,
    )


async def list_sources_with_subscribers(conn: Connection) -> list[Record]:
    return await conn.fetch(
        """
        SELECT ts.source_id, ts.source_type
        FROM title_sources ts
        WHERE EXISTS (
            SELECT 1 
            FROM subscriptions s
            WHERE ts.title_row_id = s.title_row_id
        )
        ORDER BY ts.last_checked_datetime NULLS FIRST
        """,
    )
