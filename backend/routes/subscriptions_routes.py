from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from clients import MangadexClient
from controllers import subscriptions_controller
from dependencies import CurrentUser, DbPool, get_mangadex_client
from exceptions import (
    MangadexError,
    MangadexNotFoundError,
    SubscriptionNotFoundError,
)
from models import SourceType, TitleStatus

router = APIRouter(prefix="/subscriptions")


class SubscriptionRequest(BaseModel):
    source_id: str
    source_type: SourceType


class SubscriptionResponse(BaseModel):
    subscription_public_id: UUID


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: SubscriptionRequest,
    client: Annotated[MangadexClient, Depends(get_mangadex_client)],
    user: CurrentUser,
    pool: DbPool,
) -> SubscriptionResponse:
    if subscription.source_type != "MANGADEX":
        raise HTTPException(status_code=400, detail="Not supported yet")

    try:
        subscription_public_id = await subscriptions_controller.add_subscription(
            pool,
            client,
            user["row_id"],
            subscription.source_id,
            subscription.source_type,
        )
        return SubscriptionResponse(subscription_public_id=subscription_public_id)
    except MangadexNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MangadexError as e:
        raise HTTPException(status_code=502, detail=str(e))


class SubscriptionItem(BaseModel):
    title_public_id: UUID
    title_name: str
    cover_url: str | None
    title_status: TitleStatus
    latest_read_chapter: Decimal | None
    latest_free_chapter: Decimal | None
    read_url: str | None
    subscription_public_id: UUID
    has_new_chapter: bool


@router.get("")
async def list_subscriptions(user: CurrentUser, pool: DbPool) -> list[SubscriptionItem]:
    rows = await subscriptions_controller.get_subscriptions(pool, user["row_id"])
    return [SubscriptionItem(**dict(row)) for row in rows]


class SubscriptionUpdateRequest(BaseModel):
    latest_read_chapter: Decimal | None = None
    read_url: str | None = None


@router.patch("/{subscription_public_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_subscription(
    update: SubscriptionUpdateRequest,
    subscription_public_id: UUID,
    user: CurrentUser,
    pool: DbPool,
) -> None:
    try:
        await subscriptions_controller.update_subscription(
            pool,
            user["row_id"],
            subscription_public_id,
            update.latest_read_chapter,
            update.read_url,
        )
    except SubscriptionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{subscription_public_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_public_id: UUID, user: CurrentUser, pool: DbPool
) -> None:
    try:
        await subscriptions_controller.remove_subscription(
            pool, user["row_id"], subscription_public_id
        )
    except SubscriptionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
