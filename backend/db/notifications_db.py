from datetime import datetime
from decimal import Decimal
from uuid import UUID

from asyncpg import Connection, Record


async def create_notifications(
    conn: Connection, title_row_id: int, chapter: Decimal
) -> None:
    await conn.execute(
        """
        INSERT INTO notifications (user_row_id, title_row_id, chapter)
        SELECT s.user_row_id, $1, $2
        FROM subscriptions s
        WHERE s.title_row_id = $1 AND COALESCE(s.latest_notified_chapter, 0) < $2 
            AND COALESCE(s.latest_read_chapter, 0) < $2
        """,
        title_row_id,
        chapter,
    )


async def list_notifications(
    conn: Connection, user_row_id: int, unseen_only: bool, limit: int
) -> list[Record]:
    return await conn.fetch(
        """
        SELECT n.notification_public_id, t.title_name, t.cover_url, n.chapter, n.seen_datetime, n.create_datetime
        FROM notifications n
        JOIN titles t ON n.title_row_id = t.row_id
        WHERE n.user_row_id = $1
            AND (NOT $2 OR n.seen_datetime IS NULL)
        ORDER BY (n.seen_datetime IS NULL) DESC, n.create_datetime DESC
        LIMIT $3
        """,
        user_row_id,
        unseen_only,
        limit,
    )


async def set_notification_seen(
    conn: Connection, user_row_id: int, notification_public_id: UUID
) -> UUID | None:
    return await conn.fetchval(
        """
        UPDATE notifications
        SET seen_datetime = COALESCE(seen_datetime, now())
        WHERE user_row_id = $1 AND notification_public_id = $2
        RETURNING notification_public_id
        """,
        user_row_id,
        notification_public_id,
    )


async def set_all_notifications_seen(conn: Connection, user_row_id: int) -> None:
    await conn.execute(
        """
        UPDATE notifications 
        SET seen_datetime = now()
        WHERE user_row_id = $1 AND seen_datetime IS NULL
        """,
        user_row_id,
    )


async def count_unseen_notifications(conn: Connection, user_row_id: int) -> int:
    return await conn.fetchval(
        """
        SELECT COUNT(*)
        FROM notifications 
        WHERE user_row_id = $1 AND seen_datetime IS NULL
        """,
        user_row_id,
    )
