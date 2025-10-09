# ruff: noqa: E712
# pylint: disable=duplicate-code
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User as UserModel
from app.modules.products.schemas import Product as ProductSchema, ProductCreate
from app.core.dependencies import get_async_db
from app.modules.users.auth import get_current_seller
from app.modules.products.crud import (
    crud_get_product,
    crud_get_products,
    crud_get_products_by_category,
    crud_create_product,
    crud_update_product,
    crud_delete_product,
)
from app.modules.categories.crud import crud_get_category

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products(db: AsyncSession = Depends(get_async_db)):
    """Возвращает список всех товаров."""
    products_db = await crud_get_products(db)
    return products_db


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_create: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller),
):
    """Создает новый товар."""
    if product_create.category_id is not None:
        category = await crud_get_category(product_create.category_id, db)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категории с ID {product_create.category_id} не существует",
            )
    product_db = await crud_create_product(product_create, db, current_user)
    return product_db


@router.get(
    "/category/{category_id}",
    response_model=list[ProductSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    category_id: Annotated[int, Path(..., ge=1)],
    db: AsyncSession = Depends(get_async_db),
):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    category = await crud_get_category(category_id, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категории с ID {category_id} не существует",
        )

    products_db = await crud_get_products_by_category(category_id, db)
    return products_db


@router.get(
    "/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK
)
async def get_product(
    product_id: Annotated[int, Path(..., ge=1)],
    db: AsyncSession = Depends(get_async_db),
):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    product = await crud_get_product(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Продукта с ID {product_id} не существует",
        )
    if product.category_id is not None:
        category = await crud_get_category(product.category_id, db)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категории с ID {product.category_id} не существует",
            )
    return product


@router.put(
    "/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK
)
async def update_product(
    product_id: Annotated[int, Path(..., ge=1)],
    product_update: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller),
):
    """Обновляет товар по ID."""
    product = await crud_get_product(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Продукта с ID {product_id} не существует",
        )
    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own products",
        )
    if product.category_id is not None:
        category = await crud_get_category(product.category_id, db)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Категории с ID {product.category_id} не существует",
            )

    product_db = await crud_update_product(product_id, product_update, db)
    return product_db


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: Annotated[int, Path(..., ge=1)],
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller),
):
    """Удаляет продукт по ID."""
    product = await crud_get_product(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Продукта с ID {product_id} не существует",
        )
    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own products",
        )
    if product.category_id is not None:
        category = await crud_get_category(product.category_id, db)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Категории с ID {product.category_id} не существует",
            )
    success = await crud_delete_product(product_id, db)

    if success:
        return {"status": "success", "message": "Product marked as inactive"}
    return {"status": "error", "message": "Don't access marked product as inactive"}
