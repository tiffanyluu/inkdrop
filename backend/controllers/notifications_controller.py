from uuid import UUID

from asyncpg import Pool, Record

from exceptions import NotificationNotFoundError
from db import notifications_db


async def get_notifications(
    pool: Pool, user_row_id: int, unseen_only: bool, limit: int
) -> list[Record]:
    async with pool.acquire() as conn:
        return await notifications_db.list_notifications(
            conn, user_row_id, unseen_only, limit
        )


async def mark_notification_seen(
    pool: Pool, user_row_id: int, notification_public_id: UUID
) -> None:
    async with pool.acquire() as conn:
        val = await notifications_db.set_notification_seen(
            conn, user_row_id, notification_public_id
        )

    if val is None:
        raise NotificationNotFoundError("Notification was not found")


async def mark_all_notifications_seen(pool: Pool, user_row_id: int) -> None:
    async with pool.acquire() as conn:
        await notifications_db.set_all_notifications_seen(conn, user_row_id)


async def get_unseen_count(pool: Pool, user_row_id: int) -> int:
    async with pool.acquire() as conn:
        return await notifications_db.count_unseen_notifications(conn, user_row_id)
