# ruff: noqa: E712
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.users import User as UserModel
from app.schemas.users import UserCreate
from app.auth.security import verify_password, hash_password


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        """
        Получает пользователя по id
        """
        result = await self.db.scalars(
            select(UserModel).where(
                UserModel.id == user_id, UserModel.is_active == True
            )
        )
        user = result.first()
        return user

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """
        Получает пользователя по email
        """
        result = await self.db.scalars(
            select(UserModel).where(
                UserModel.email == email, UserModel.is_active == True
            )
        )
        user = result.first()
        return user

    async def create(self, user: UserCreate) -> UserModel:
        """
        Регистрирует нового пользователя с ролью 'buyer' или 'seller'.
        """
        db_user = UserModel(
            email=user.email,
            hashed_password=hash_password(user.password),
            role=user.role,
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update(self, user_id: int, user_update: UserCreate) -> UserModel:
        """
        Обновляет пользователя по id
        """
        result = await self.db.execute(
            update(UserModel).where(UserModel.id == user_id).values(**user_update)
        )
        await self.db.commit()
        if result.rowcount > 0:
            return await self.get_by_id(user_id)
        return None

    async def delete(self, user_id: int) -> bool:
        """
        Мягкое удаление пользователя.
        """
        result = await self.db.execute(
            update(UserModel).where(UserModel.id == user_id).values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def authenticate(self, email: str, password: str):
        """Аутентифицирует пользователя"""
        user = await self.get_user_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
