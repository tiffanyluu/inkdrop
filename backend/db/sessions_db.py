from datetime import datetime

from asyncpg import Connection, Record


async def create_session(
    conn: Connection, user_row_id: int, token_hash: str, expiration_datetime: datetime
) -> None:
    await conn.execute(
        """
        INSERT INTO user_sessions (token_hash, user_row_id, expiration_datetime)
        VALUES ($1, $2, $3)
        """,
        token_hash,
        user_row_id,
        expiration_datetime,
    )


async def get_user_by_token_hash(conn: Connection, token_hash: str) -> Record | None:
    return await conn.fetchrow(
        """
        SELECT u.row_id, u.user_public_id, u.email, u.first_name, u.last_name
        FROM users u JOIN user_sessions s ON u.row_id = s.user_row_id
        WHERE s.token_hash = $1 AND s.expiration_datetime > now()
        """,
        token_hash,
    )


async def delete_session(conn: Connection, token_hash: str) -> None:
    await conn.execute(
        """
        DELETE FROM user_sessions WHERE token_hash = $1
        """,
        token_hash,
    )
