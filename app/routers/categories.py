# ruff: noqa: E712
# pylint: disable=duplicate-code
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category as CategoryModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.dependencies.db import get_async_db

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategorySchema], status_code=status.HTTP_200_OK)
async def get_categories(db: AsyncSession = Depends(get_async_db)):
    """Возвращает список всех категорий товаров."""
    result = await db.scalars(
        select(CategoryModel).where(CategoryModel.is_active == True)
    )
    categories = result.all()
    return categories


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_create: CategoryCreate, db: AsyncSession = Depends(get_async_db)
):
    """Создает новую категорию."""
    if category_create.parent_id is not None:
        stmt = select(CategoryModel).where(
            CategoryModel.id == category_create.parent_id,
            CategoryModel.is_active == True,
        )
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )

    category = CategoryModel(**category_create.model_dump())
    db.add(category)
    await db.commit()
    return category


@router.put(
    "/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK
)
async def update_category(
    category_id: Annotated[int, Path(..., ge=1)],
    category_update: CategoryCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Обновляет новую категорию по ее ID."""
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active == True
    )
    result = await db.scalars(stmt)
    category = result.first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if category.parent_id is not None:
        stmt = select(CategoryModel).where(
            CategoryModel.parent_id == category.parent_id,
            CategoryModel.is_active == True,
        )
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category_update.model_dump())
    )
    await db.commit()
    return category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: Annotated[int, Path(..., ge=1)],
    db: AsyncSession = Depends(get_async_db),
):
    """Удаляет категорию по ее ID."""
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active == True
    )
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Категории с ID {category_id} не существует",
        )
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(is_active=False)
    )
    await db.commit()

    return {"status": "success", "message": "Category marked as inactive"}
