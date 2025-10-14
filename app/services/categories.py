from typing import Optional
from app.repositories.categories import CategoryRepository
from app.schemas.categories import CategoryCreate
from app.models.categories import Category as CategoryModel
from app.core.exceptions import NotFoundException, ConflictException


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    async def get_all_categories(self) -> list[CategoryModel]:
        db_categories = await self.category_repo.get_all()
        return db_categories

    async def get_category_by_id(self, category_id: int) -> Optional[CategoryModel]:
        db_category = await self.category_repo.get_by_id(category_id)
        if not db_category:
            raise NotFoundException(f"Category with id {category_id} not found")
        return db_category

    async def create_category(
        self, category: CategoryCreate
    ) -> Optional[CategoryModel]:
        if category.parent_id == 0:
            category.parent_id = None
        if category.parent_id:
            parent = await self.category_repo.get_by_id(category.parent_id)
            if not parent:
                raise NotFoundException(
                    f"Parent category with id {category.parent_id} not found"
                )
        exsiting_category = await self.category_repo.get_by_name(category.name)
        if exsiting_category:
            raise ConflictException(f"Category '{category.name}' already exists")
        category_db = await self.category_repo.create(category)
        return category_db

    async def update_category(
        self, category_id: int, category: CategoryCreate
    ) -> CategoryModel:
        if category.parent_id == 0:
            category.parent_id = None
        exsiting_category = await self.category_repo.get_by_id(category_id)
        if not exsiting_category:
            raise NotFoundException(f"Category with id {category_id} not found")
        if category.name != exsiting_category.name:
            category_with_same_name = await self.category_repo.get_by_name(
                category.name
            )
            if category_with_same_name:
                raise ConflictException(f"Category '{category.name}' already exists")
        return await self.category_repo.update(category_id, category)

    async def delete_category(self, category_id: int) -> bool:
        existing_category = await self.category_repo.get_by_id(category_id)
        if not existing_category:
            raise NotFoundException(
                f"Category with id {category_id} has been deleted or not existing"
            )
        return await self.category_repo.delete(category_id)
