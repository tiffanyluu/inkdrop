from uuid import UUID

from asyncpg import Connection, Record

from exceptions import NotificationNotFoundError
from db import notifications_db


async def get_notifications(
    conn: Connection, user_row_id: int, unseen_only: bool, limit: int
) -> list[Record]:
    return await notifications_db.list_notifications(
        conn, user_row_id, unseen_only, limit
    )


async def mark_notification_seen(
    conn: Connection, user_row_id: int, notification_public_id: UUID
) -> None:
    val = await notifications_db.set_notification_seen(
        conn, user_row_id, notification_public_id
    )

    if val is None:
        raise NotificationNotFoundError("Notification was not found")


async def mark_all_notifications_seen(conn: Connection, user_row_id: int) -> None:
    await notifications_db.set_all_notifications_seen(conn, user_row_id)


async def get_unseen_count(conn: Connection, user_row_id: int) -> int:
    return await notifications_db.count_unseen_notifications(conn, user_row_id)
