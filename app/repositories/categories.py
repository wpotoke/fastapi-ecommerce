# ruff: noqa: E712
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category as CategoryModel
from app.schemas.categories import CategoryCreate


class CategoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[CategoryModel]:
        """Возвращает список всех категорий товаров."""
        result = await self.db.scalars(
            select(CategoryModel).where(CategoryModel.is_active == True)
        )
        categories = result.all()
        return categories

    async def get_by_id(self, category_id: int) -> Optional[CategoryModel]:
        stmt = select(CategoryModel).where(
            CategoryModel.id == category_id, CategoryModel.is_active == True
        )
        result = await self.db.scalars(stmt)
        category = result.first()
        return category

    async def get_parent_id(self, parent_id: int) -> Optional[CategoryModel]:
        stmt = select(CategoryModel).where(
            CategoryModel.parent_id == parent_id, CategoryModel.is_active == True
        )
        result = await self.db.scalars(stmt)
        category = result.first()
        return category

    async def get_by_name(self, name: str) -> Optional[CategoryModel]:
        stmt = select(CategoryModel).where(
            CategoryModel.name == name, CategoryModel.is_active == True
        )
        result = await self.db.scalars(stmt)
        category = result.first()
        return category

    async def create(self, category_create: CategoryCreate) -> CategoryModel:
        """Создает новую категорию."""
        category = CategoryModel(**category_create.model_dump())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def update(
        self,
        category_id: int,
        category_update: CategoryCreate,
    ) -> Optional[CategoryModel]:
        """Обновляет новую категорию по ее ID."""
        result = await self.db.execute(
            update(CategoryModel)
            .where(CategoryModel.id == category_id)
            .values(**category_update.model_dump())
        )
        await self.db.commit()
        if result.rowcount > 0:
            return await self.get_by_id(category_id)
        return None

    async def delete(
        self,
        category_id: int,
    ) -> bool:
        """Удаляет категорию по ее ID."""

        result = await self.db.execute(
            update(CategoryModel)
            .where(CategoryModel.id == category_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0
