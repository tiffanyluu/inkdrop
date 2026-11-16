from decimal import Decimal
from uuid import UUID

from asyncpg import Connection, Record


async def create_subscription(
    conn: Connection, user_row_id: int, title_row_id: int
) -> UUID:
    return await conn.fetchval(
        """
        INSERT INTO subscriptions (user_row_id, title_row_id, latest_notified_chapter)
        SELECT $1, $2, MAX(title_sources.latest_free_chapter)
        FROM title_sources
        WHERE title_sources.title_row_id = $2 
        RETURNING subscription_public_id
        """,
        user_row_id,
        title_row_id,
    )


async def get_subscription_public_id(
    conn: Connection, user_row_id: int, title_row_id: int
) -> UUID:
    return await conn.fetchval(
        """
        SELECT subscription_public_id FROM subscriptions
        WHERE user_row_id = $1 AND title_row_id = $2
        """,
        user_row_id,
        title_row_id,
    )


async def list_subscriptions(conn: Connection, user_row_id: int) -> list[Record]:
    return await conn.fetch(
        """
        SELECT
            s.subscription_public_id,
            t.title_public_id,
            t.title_name,
            t.cover_url,
            t.title_status,
            s.latest_read_chapter,
            s.read_url,
            MAX(ts.latest_free_chapter) AS latest_free_chapter,
            COALESCE(
                MAX(ts.latest_free_chapter) > COALESCE(s.latest_read_chapter, 0),
                false
            ) AS has_new_chapter
        FROM subscriptions s
        JOIN titles t ON s.title_row_id = t.id
        JOIN title_sources ts ON t.id = ts.title_row_id
        WHERE s.user_row_id = $1
        GROUP BY t.id, s.id
        ORDER BY
            MAX(ts.latest_free_chapter_datetime) DESC NULLS LAST,
            t.title_name ASC
        """,
        user_row_id,
    )


async def update_subscription(
    conn: Connection,
    user_row_id: int,
    subscription_public_id: UUID,
    latest_read_chapter: Decimal | None,
    read_url: str | None,
) -> UUID | None:
    return await conn.fetchval(
        """
        UPDATE subscriptions
        SET latest_read_chapter = COALESCE($3, latest_read_chapter),
            read_url = COALESCE($4, read_url)
        WHERE user_row_id = $1 AND subscription_public_id = $2
        RETURNING subscription_public_id
        """,
        user_row_id,
        subscription_public_id,
        latest_read_chapter,
        read_url,
    )


async def delete_subscription(
    conn: Connection, user_row_id: int, subscription_public_id: UUID
) -> UUID | None:
    return await conn.fetchval(
        """
        DELETE FROM subscriptions
        WHERE user_row_id = $1 AND subscription_public_id = $2
        RETURNING subscription_public_id
        """,
        user_row_id,
        subscription_public_id,
    )
