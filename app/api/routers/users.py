# pylint:disable=bad-exception-cause,catching-non-exception
# ruff:noqa:E712
from typing import Annotated
from fastapi import APIRouter, Depends, status, Path
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import Field
from app.schemas.users import UserCreate, User
from app.auth.dependencies.services import get_user_service
from app.services.users import UserService
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    get_email_current_user,
)
from app.schemas.tokens import TokenGroup, RefreshTokenRequest


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: Annotated[UserCreate, Field(description="User create data")],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.create_user(user=user)


@router.put("/edit/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: Annotated[int, Path(ge=1)],
    user: Annotated[UserCreate, Field(description="User create data")],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.update_user(user_id=user_id, user=user)


@router.post("/token", status_code=status.HTTP_200_OK)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    Аутентифицирует пользователя и возвращает JWT с email, role и id.
    """
    user = await user_service.authenticate_user(form_data.username, form_data.password)

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


@router.post("/refresh_token", response_model=TokenGroup)
async def update_access_token(
    request: RefreshTokenRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    token_group = await user_service.refresh_access_token(
        refresh_token=request.refresh_token
    )
    return token_group


@router.get("users/me", response_model=User, status_code=status.HTTP_200_OK)
async def get_me(
    user_service: Annotated[UserService, Depends(get_user_service)],
    user_email: Annotated[str, Depends(get_email_current_user)],
):
    user = await user_service.get_user_by_email(user_email)
    return user
