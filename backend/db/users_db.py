from asyncpg import Connection, Record


async def create_user(
    conn: Connection, first_name: str, last_name: str, email: str, hashed_password: str
) -> Record:
    return await conn.fetchrow(
        """
        INSERT INTO users (first_name, last_name, email, password_hash)
        VALUES ($1, $2, $3, $4)
        RETURNING first_name, last_name, email, user_public_id
        """,
        first_name,
        last_name,
        email,
        hashed_password,
    )


async def get_user_by_email(conn: Connection, email: str) -> Record | None:
    return await conn.fetchrow(
        """
        SELECT row_id, password_hash
        FROM users WHERE lower(email) = $1
        """,
        email,
    )
