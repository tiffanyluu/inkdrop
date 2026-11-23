import asyncio
import secrets
from datetime import UTC, datetime, timedelta

from asyncpg import Connection, Record, UniqueViolationError
from pwdlib import PasswordHash

from redis.asyncio import Redis
import utils
from db import sessions_db, users_db
from exceptions import EmailAlreadyExistsError, InvalidCredentialsError

password_hasher = PasswordHash.recommended()


async def hash_password(password: str) -> str:
    hashed_password = await asyncio.to_thread(password_hasher.hash, password)
    return hashed_password


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    is_verified = await asyncio.to_thread(
        password_hasher.verify, plain_password, hashed_password
    )
    return is_verified


async def add_user(
    conn: Connection, first_name: str, last_name: str, email: str, password: str
) -> Record:
    hashed_password = await hash_password(password)
    email = email.lower()
    try:
        return await users_db.create_user(
            conn, first_name, last_name, email, hashed_password
        )
    except UniqueViolationError:
        raise EmailAlreadyExistsError("This email already exists. Please log in.")


async def login_user(
    conn: Connection,
    redis: Redis,
    email: str,
    password: str,
    session_duration: timedelta,
) -> str:
    email = email.lower()
    user = await users_db.get_user_by_email(conn, email)
    if not user:
        raise InvalidCredentialsError("Invalid email or password. Please try again.")

    is_password_verified = await verify_password(password, user["password_hash"])
    if not is_password_verified:
        raise InvalidCredentialsError("Invalid email or password. Please try again.")

    token = secrets.token_urlsafe(32)
    hashed_token = utils.hash_token(token)

    await sessions_db.create_session(
        redis, user["row_id"], hashed_token, session_duration
    )

    return token


async def logout_user(redis: Redis, token: str | None) -> None:
    if token is None:
        return
    hashed_token = utils.hash_token(token)
    await sessions_db.delete_session(redis, hashed_token)
