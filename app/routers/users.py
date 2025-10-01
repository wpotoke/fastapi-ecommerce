# pylint:disable=bad-exception-cause,catching-non-exception
# ruff:noqa:E712
import jwt

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import User as UserModel
from app.schemas import UserCreate, User as UserSchema
from app.dependencies.db import get_async_db
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрирует нового пользователя с ролью 'buyer' или 'seller'.
    """

    result = await db.scalars(select(UserModel).where(UserModel.email == user.email))
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    db_user = UserModel(
        email=user.email, hashed_password=hash_password(user.password), role=user.role
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/token")
async def login(
    form_date: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Аутентифицирует пользователя и возвращает JWT с email, role и id.
    """
    result = await db.scalars(
        select(UserModel).where(UserModel.email == form_date.username)
    )
    user = result.first()
    if not user or not verify_password(form_date.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.exceptions as e:
        raise credentials_exception from e
    result = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True)
    )
    user = result.first()
    if user is None:
        raise credentials_exception
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}
