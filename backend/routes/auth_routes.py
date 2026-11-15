from datetime import timedelta
from typing import Annotated
from uuid import UUID

from asyncpg import Record
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field

from controllers import auth_controller
from dependencies import DbPool, get_current_user
from exceptions import EmailAlreadyExistsError, InvalidCredentialsError

router = APIRouter(prefix="/auth")

SESSION_DURATION = timedelta(days=7)


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    user_public_id: UUID
    email: EmailStr
    first_name: str
    last_name: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user: SignupRequest, pool: DbPool) -> UserResponse:
    try:
        async with pool.acquire() as conn:
            fetched_user = await auth_controller.add_user(
                conn, user.first_name, user.last_name, user.email, user.password
            )
            return UserResponse(
                user_public_id=fetched_user["user_public_id"],
                email=fetched_user["email"],
                first_name=fetched_user["first_name"],
                last_name=fetched_user["last_name"],
            )
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/me")
async def get_user(user: Annotated[Record, Depends(get_current_user)]) -> UserResponse:
    return UserResponse(
        user_public_id=user["user_public_id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login_user(user: LoginRequest, response: Response, pool: DbPool) -> None:
    try:
        async with pool.acquire() as conn:
            token = await auth_controller.login_user(
                conn, user.email, user.password, SESSION_DURATION
            )
            response.set_cookie(
                key="session",
                value=token,
                httponly=True,
                samesite="lax",
                max_age=int(SESSION_DURATION.total_seconds()),
                secure=True,
            )
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    response: Response,
    pool: DbPool,
    session: Annotated[str | None, Cookie()] = None,
) -> None:
    async with pool.acquire() as conn:
        await auth_controller.logout_user(
            conn,
            session,
        )
    response.delete_cookie(
        "session",
        httponly=True,
        samesite="lax",
        secure=True,
    )
