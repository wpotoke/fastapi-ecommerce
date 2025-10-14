from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.repositories.categories import CategoryRepository
from app.repositories.products import ProductRepository
from app.repositories.reviews import ReviewRepository

from app.core.dependencies.db import get_async_db


def get_category_repository(
    db: AsyncSession = Depends(get_async_db),
) -> CategoryRepository:
    return CategoryRepository(db=db)


def get_product_repository(
    db: AsyncSession = Depends(get_async_db),
) -> CategoryRepository:
    return ProductRepository(db=db)


def get_review_repository(
    db: AsyncSession = Depends(get_async_db),
) -> CategoryRepository:
    return ReviewRepository(db=db)
