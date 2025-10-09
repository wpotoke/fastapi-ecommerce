# pylint:disable=bad-exception-cause,catching-non-exception
# ruff:noqa:E712
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User as UserModel
from app.modules.users.schemas import UserCreate, User as UserSchema
from app.core.dependencies import get_async_db
from app.modules.users.auth import (
    create_access_token,
    create_refresh_token,
)
from app.modules.users.crud import (
    crud_create_user,
    crud_get_user_by_email,
)
from app.modules.users.auth import (
    authenticate_user,
    refresh_access_token_service,
    get_current_user,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрирует нового пользователя с ролью 'buyer' или 'seller'.
    """

    user_db = await crud_get_user_by_email(user.email, db)
    if user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user_db = await crud_create_user(user, db)
    return user_db


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Аутентифицирует пользователя и возвращает JWT с email, role и id.
    """
    user = await authenticate_user(form_data.username, form_data.password, db)

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh_token")
async def update_access_token(
    refresh_token: str, db: AsyncSession = Depends(get_async_db)
):
    """
    Обновляет access_token с помощью refresh_token.
    """
    return await refresh_access_token_service(refresh_token, db)


@router.get("/me", response_model=UserCreate)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """Получить текущего пользователя"""
    return current_user
