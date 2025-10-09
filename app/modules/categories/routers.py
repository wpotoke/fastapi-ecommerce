# ruff: noqa: E712
# pylint: disable=duplicate-code
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.schemas import Category as CategorySchema, CategoryCreate
from app.core.dependencies import get_async_db
from app.modules.categories.crud import (
    crud_get_categories,
    crud_get_category,
    crud_create_category,
    crud_update_category,
    crud_delete_category,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategorySchema], status_code=status.HTTP_200_OK)
async def get_categories(db: AsyncSession = Depends(get_async_db)):
    """Возвращает список всех категорий товаров."""
    categories_db = await crud_get_categories(db)
    return categories_db


@router.get(
    "/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK
)
async def get_category(
    category_id: Annotated[int, Path(ge=1)], db: AsyncSession = Depends(get_async_db)
):
    """Возвращает список всех категорий товаров."""
    category = await crud_get_category(category_id, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_create: CategoryCreate, db: AsyncSession = Depends(get_async_db)
):
    """Создает новую категорию."""
    if category_create.parent_id is not None:
        parent = await crud_get_category(category_create.id, db)
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )

    category_db = await crud_create_category(category_create, db)
    return category_db


@router.put(
    "/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK
)
async def update_category(
    category_id: Annotated[int, Path(..., ge=1)],
    category_update: CategoryCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Обновляет новую категорию по ее ID."""
    category = await crud_get_category(category_id, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if category_update.parent_id is not None:
        parent = await crud_get_category(category_update.parent_id, db)
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )
    category_db = await crud_update_category(category_id, category_update, db)
    return category_db


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: Annotated[int, Path(..., ge=1)],
    db: AsyncSession = Depends(get_async_db),
):
    """Удаляет категорию по ее ID."""
    category = await crud_get_category(category_id, db)
    if category is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Категории с ID {category_id} не существует",
        )
    success = await crud_delete_category(category_id, db)

    if success:
        return {"status": "success", "message": "Category marked as inactive"}
    return {"status": "error", "message": "Don't access marked category as inactive"}
