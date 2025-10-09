# ruff: noqa: E712
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.models import Category as CategoryModel
from app.modules.categories.schemas import CategoryCreate


async def crud_get_categories(db: AsyncSession):
    """Возвращает список всех категорий товаров."""
    result = await db.scalars(
        select(CategoryModel).where(CategoryModel.is_active == True)
    )
    categories = result.all()
    return categories


async def crud_get_category(category_id: int, db: AsyncSession):
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active == True
    )
    result = await db.scalars(stmt)
    category = result.first()
    return category


async def crud_create_category(category_create: CategoryCreate, db: AsyncSession):
    """Создает новую категорию."""
    category = CategoryModel(**category_create.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def crud_update_category(
    category_id: int,
    category_update: CategoryCreate,
    db: AsyncSession,
):
    """Обновляет новую категорию по ее ID."""
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category_update.model_dump())
    )
    await db.commit()
    return await crud_get_category(category_id, db)


async def crud_delete_category(
    category_id: int,
    db: AsyncSession,
):
    """Удаляет категорию по ее ID."""

    result = await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(is_active=False)
    )
    await db.commit()
    return result.rowcount > 0
