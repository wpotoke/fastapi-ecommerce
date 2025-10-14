from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.repositories.users import UserRepository
from app.core.dependencies.db import get_async_db


def get_user_repository(db: AsyncSession = Depends(get_async_db)) -> UserRepository:
    return UserRepository(db=db)
