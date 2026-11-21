from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID
from exceptions import NotificationNotFoundError
from controllers import notifications_controller
from dependencies import CurrentUser, DbPool


from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

router = APIRouter(prefix="/notifications")


class NotificationItem(BaseModel):
    notification_public_id: UUID
    title_name: str
    cover_url: str | None
    chapter: Decimal
    seen_datetime: datetime | None
    create_datetime: datetime


@router.get("")
async def list_notifications(
    user: CurrentUser,
    pool: DbPool,
    unseen_only: bool = False,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[NotificationItem]:
    async with pool.acquire() as conn:
        notifications = await notifications_controller.get_notifications(
            conn, user["row_id"], unseen_only, limit
        )
        return [
            NotificationItem(**dict(notification)) for notification in notifications
        ]


@router.post("/seen-all", status_code=status.HTTP_204_NO_CONTENT)
async def set_all_notifications_seen(user: CurrentUser, pool: DbPool) -> None:
    async with pool.acquire() as conn:
        await notifications_controller.mark_all_notifications_seen(conn, user["row_id"])


class UnseenNotificationsCount(BaseModel):
    count: int


@router.get("/unseen-count")
async def count_unseen_notifications(
    user: CurrentUser, pool: DbPool
) -> UnseenNotificationsCount:
    async with pool.acquire() as conn:
        count = await notifications_controller.get_unseen_count(conn, user["row_id"])
        return UnseenNotificationsCount(count=count)


@router.patch("/{notification_public_id}", status_code=status.HTTP_204_NO_CONTENT)
async def set_notification_seen(
    user: CurrentUser, pool: DbPool, notification_public_id: UUID
) -> None:
    try:
        async with pool.acquire() as conn:
            await notifications_controller.mark_notification_seen(
                conn, user["row_id"], notification_public_id
            )
    except NotificationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
