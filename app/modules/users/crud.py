# ruff: noqa: E712
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.modules.users.models import User as UserModel
from app.modules.users.schemas import UserCreate
from app.modules.users.utils import hash_password


async def crud_get_user(user_id: int, db: AsyncSession):
    """
    Получает пользователя по id
    """
    result = await db.scalars(
        select(UserModel).where(UserModel.id == user_id, UserModel.is_active == True)
    )
    user = result.first()
    return user


async def crud_get_user_by_email(email: str, db: AsyncSession):
    """
    Получает пользователя по email
    """
    result = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True)
    )
    user = result.first()
    return user


async def crud_create_user(user: UserCreate, db: AsyncSession):
    """
    Регистрирует нового пользователя с ролью 'buyer' или 'seller'.
    """
    db_user = UserModel(
        email=user.email, hashed_password=hash_password(user.password), role=user.role
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def crud_update_user(user_id: int, user_update: UserCreate, db: AsyncSession):
    """
    Обновляет пользователя по id
    """
    await db.execute(
        update(UserModel)
        .where(UserModel.id == user_id)
        .values(**user_update.model_dump())
    )
    await db.commit()
    return await crud_get_user(user_id, db)


async def crud_delete_user(user_id: int, db: AsyncSession):
    """
    Мягкое удаление пользователя.
    """
    result = await db.execute(
        update(UserModel).where(UserModel.id == user_id).values(is_active=False)
    )
    await db.commit()
    return result.rowcount > 0
