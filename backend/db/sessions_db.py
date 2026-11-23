from datetime import timedelta
from redis.asyncio import Redis


async def create_session(
    redis: Redis, user_row_id: int, token_hash: str, session_duration: timedelta
) -> None:
    await redis.set(f"session:{token_hash}", user_row_id, ex=session_duration)


async def get_user_row_id(redis: Redis, token_hash: str) -> int | None:
    val = await redis.get(f"session:{token_hash}")
    if val is not None:
        return int(val)
    return val


async def delete_session(redis: Redis, token_hash: str) -> None:
    await redis.delete(f"session:{token_hash}")
