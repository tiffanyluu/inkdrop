from datetime import datetime
from decimal import Decimal
from uuid import UUID
import asyncpg


async def create_title(
    conn: asyncpg.Connection,
    name: str,
    status: str,
    cover_url: str | None,
    description: str | None,
) -> asyncpg.Record:
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
    conn: asyncpg.Connection,
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
    conn: asyncpg.Connection, source_type: str, source_id: str
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
