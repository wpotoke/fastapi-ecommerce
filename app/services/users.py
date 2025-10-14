# ruff: noqa: E712
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.models.users import User as UserModel
from app.schemas.users import UserCreate
from app.repositories.users import UserRepository
from app.auth.security import (
    create_access_token,
    hash_password,
    get_email_refresh_access_token,
)
from app.core.exceptions import NotFoundException, ConflictException, BusinessException
from app.schemas.tokens import TokenGroup, RefreshTokenBase
from app.core.config import settings


class UserService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user(self, user_id: int) -> Optional[UserModel]:
        user_db = await self.user_repo.get_by_id(user_id)
        if not user_db:
            raise NotFoundException(f"User with id {user_id} not found")
        return user_db

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        user_db = await self.user_repo.get_user_by_email(email)
        if not user_db:
            raise NotFoundException("User with this email not found")
        return user_db

    async def create_user(self, user: UserCreate) -> UserModel:
        existing_user_email = await self.user_repo.get_user_by_email(user.email)
        if existing_user_email:
            raise ConflictException("User already exists")
        user_db = await self.user_repo.create(user)
        return user_db

    async def update_user(
        self, user_id: int, user_update: UserCreate
    ) -> Optional[UserModel]:
        user_db = await self.user_repo.get_by_id(user_id)
        if not user_db:
            raise NotFoundException(f"User with id {user_id} not found")

        modified_data = user_update.model_dump(exclude_unset=True)
        if "password" in modified_data:
            modified_data["hashed_password"] = hash_password(modified_data["password"])
            del modified_data["password"]

        user_upt_db = await self.user_repo.update(user_id, modified_data)
        return user_upt_db

    async def delete_user(self, user_id: int) -> bool:
        user_db = await self.user_repo.get_by_id(user_id)
        if not user_db:
            raise NotFoundException(f"User with id {user_id} not found")
        return await self.user_repo.delete(user_id)

    async def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        authed_user = await self.user_repo.authenticate(email, password)
        if not authed_user:
            raise BusinessException("email or password wrong")
        return authed_user

    async def refresh_access_token(self, refresh_token: str) -> dict:
        email = await get_email_refresh_access_token(refresh_token=refresh_token)
        user = await self.get_user_by_email(email)
        if not user:
            raise NotFoundException("User with this email not found")
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role, "id": user.id}
        )

        refresh_token_schema = RefreshTokenBase(
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return TokenGroup(access_token=access_token, refresh_token=refresh_token_schema)
