# ruff: noqa: E712
# pylint: disable=duplicate-code
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.models.users import User as UserModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.dependencies.db import get_async_db
from app.auth import get_current_seller

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products(db: AsyncSession = Depends(get_async_db)):
    """Возвращает список всех товаров."""
    result = await db.scalars(
        select(ProductModel).where(ProductModel.is_active == True)
    )
    products = result.all()
    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_create: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller),
):
    """Создает новый товар."""
    if product_create.category_id is not None:
        stmt = select(CategoryModel).where(
            CategoryModel.id == product_create.category_id,
            CategoryModel.is_active == True,
        )
        result = await db.scalars(stmt)
        category = result.first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категории с ID {product_create.category_id} не существует",
            )
    product = ProductModel(**product_create.model_dump(), seller_id=current_user.id)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


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
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active == True
    )
    result = await db.scalars(stmt)
    category = result.first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категории с ID {category_id} не существует",
        )

    stmt = select(ProductModel).where(
        ProductModel.category_id == category_id, ProductModel.is_active == True
    )
    result = await db.scalars(stmt)
    products = result.all()
    return products


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
    stmt = select(ProductModel).where(
        ProductModel.id == product_id, ProductModel.is_active == True
    )
    result = await db.scalars(stmt)
    product = result.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Продукта с ID {product_id} не существует",
        )
    if product.category_id is not None:
        stmt = select(CategoryModel).where(
            CategoryModel.id == product.category_id, CategoryModel.is_active == True
        )
        result = await db.scalars(stmt)
        category = result.first()
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
    stmt = select(ProductModel).where(
        ProductModel.id == product_id, ProductModel.is_active == True
    )
    result = await db.scalars(stmt)
    product = result.first()
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
        stmt = select(CategoryModel).where(
            CategoryModel.id == product.category_id, CategoryModel.is_active == True
        )
        result = await db.scalars(stmt)
        category = result.first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Категории с ID {product.category_id} не существует",
            )

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product_update.model_dump())
    )
    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: Annotated[int, Path(..., ge=1)],
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller),
):
    """Удаляет продукт по ID."""
    stmt = select(ProductModel).where(
        ProductModel.id == product_id, ProductModel.is_active == True
    )
    result = await db.scalars(stmt)
    product = result.first()
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
        stmt = select(CategoryModel).where(
            CategoryModel.id == product.category_id, CategoryModel.is_active == True
        )
        result = await db.scalars(stmt)
        category = result.first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Категории с ID {product.category_id} не существует",
            )
    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(is_active=False)
    )
    await db.commit()
    await db.refresh(product)

    return {"status": "success ✅", "message": "Product marked as inactive"}
