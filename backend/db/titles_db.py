from datetime import datetime
from decimal import Decimal
from uuid import UUID
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
        RETURNING id, title_public_id
        """,
        name,
        cover_url,
        status,
        description,
    )


async def create_title_source(
    conn: Connection,
    title_id: int,
    source_type: str,
    source_id: str,
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
        title_id,
        source_id,
        source_type,
        latest_free_chapter,
        latest_free_chapter_datetime,
    )


async def get_title_by_source(
    conn: Connection, source_type: str, source_id: str
) -> UUID | None:
    return await conn.fetchval(
        """
        SELECT t.title_public_id FROM titles t JOIN title_sources s
        ON t.id = s.title_row_id
        WHERE s.source_type = $1 AND s.source_id = $2
        """,
        source_type,
        source_id,
    )


async def get_source_by_source_id_type(
    conn: Connection, source_id: str, source_type: str
) -> Record | None:
    return await conn.fetchrow(
        """
        SELECT s.latest_free_chapter, s.latest_free_chapter_datetime
        FROM title_sources s WHERE s.source_id = $1 AND s.source_type = $2
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
