from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies.db import get_async_db
from app.services.users import UserService
from app.repositories.users import UserRepository


def get_user_service(db: AsyncSession = Depends(get_async_db)) -> UserService:
    return UserService(user_repo=UserRepository(db=db))
