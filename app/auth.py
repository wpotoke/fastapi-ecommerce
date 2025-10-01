# ruff: noqa: E712
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt

from app.models.users import User as UserModel
from app.config import settings
from app.dependencies.db import get_async_db


# Создаём контекст для хеширования с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def hash_password(password: str) -> str:
    """
    Преобразует пароль в хеш с использованием bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли введённый пароль сохранённому хешу.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    """
    Создаёт JWT с payload (sub, role, id, exp).
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict):
    """
    Создаёт рефреш-токен с длительным сроком действия.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=int(settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)
):
    """
    Проверяет JWT и возвращает пользователя из базы.
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.PyJWTError as exc:
        raise credential_exception from exc
    result = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True)
    )
    user = result.first()
    if user is None:
        raise credential_exception
    return user


async def get_current_seller(current_user: UserModel = Depends(get_current_user)):
    """
    Проверяет, что пользователь имеет роль 'seller'.
    """
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can perform this action",
        )
    return current_user


async def get_current_buyer(current_user: UserModel = Depends(get_current_user)):
    """
    Проверяет, что пользователь имеет роль 'buyer'.
    """
    if current_user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyer can perform this action",
        )
    return current_user


async def get_admin(current_user: UserModel = Depends(get_current_user)):
    """
    Проверяет, что пользователь имеет роль 'admin'.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can perform this action",
        )
    return current_user
