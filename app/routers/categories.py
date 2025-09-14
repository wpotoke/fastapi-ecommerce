# ruff: noqa: E712
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import Category as CategoryModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.dependencies.db import get_db

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategorySchema], status_code=status.HTTP_200_OK)
async def get_categories(db: Session = Depends(get_db)):
    """Возвращает список всех категорий товаров."""
    stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    categories = db.scalars(stmt).all()
    return categories


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_create: CategoryCreate, db: Session = Depends(get_db)
):
    """Создает новую категорию."""
    if category_create.parent_id is not None:
        stmt = select(CategoryModel).where(
            CategoryModel.id == category_create.parent_id,
            CategoryModel.is_active == True,
        )
        parent = db.scalars(stmt).first()
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )

    category = CategoryModel(**category_create.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put(
    "/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK
)
async def update_category(
    category_id: Annotated[int, Path(..., ge=1)],
    category_update: CategoryCreate,
    db: Session = Depends(get_db),
):
    """Обновляет новую категорию по ее ID."""
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active == True
    )
    category = db.scalars(stmt).first()
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
        parent = db.scalars(stmt).first()
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )
    db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category_update.model_dump())
    )
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: Annotated[int, Path(..., ge=1)], db: Session = Depends(get_db)
):
    """Удаляет категорию по ее ID."""
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active == True
    )
    category = db.scalars(stmt).first()
    if category is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Категории с ID {category_id} не существует",
        )
    db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(is_active=False)
    )
    db.commit()

    return {"status": "success", "message": "Category marked as inactive"}
