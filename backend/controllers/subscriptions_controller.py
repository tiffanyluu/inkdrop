from decimal import Decimal
from uuid import UUID

from asyncpg import Pool, Record, UniqueViolationError

from clients import MangadexClient
from controllers import titles_controller
from db import subscriptions_db
from exceptions import SubscriptionNotFoundError
from models import SourceType


async def add_subscription(
    pool: Pool,
    client: MangadexClient,
    user_row_id: int,
    source_id: str,
    source_type: SourceType,
) -> UUID:
    title_row_id, _ = await titles_controller.add_title(
        pool, client, source_id, source_type
    )
    async with pool.acquire() as conn:
        try:
            return await subscriptions_db.create_subscription(
                conn,
                user_row_id,
                title_row_id,
            )
        except UniqueViolationError:
            return await subscriptions_db.get_subscription_public_id(
                conn, user_row_id, title_row_id
            )


async def get_subscriptions(pool: Pool, user_row_id: int) -> list[Record]:
    async with pool.acquire() as conn:
        return await subscriptions_db.list_subscriptions(conn, user_row_id)


async def update_subscription(
    pool: Pool,
    user_row_id: int,
    subscription_public_id: UUID,
    latest_read_chapter: Decimal | None,
    read_url: str | None,
) -> None:
    async with pool.acquire() as conn:
        val = await subscriptions_db.update_subscription(
            conn, user_row_id, subscription_public_id, latest_read_chapter, read_url
        )

    if val is None:
        raise SubscriptionNotFoundError("Subscription was not found")


async def remove_subscription(
    pool: Pool, user_row_id: int, subscription_public_id: UUID
) -> None:
    async with pool.acquire() as conn:
        val = await subscriptions_db.delete_subscription(
            conn, user_row_id, subscription_public_id
        )

    if val is None:
        raise SubscriptionNotFoundError("Subscription was not found")
