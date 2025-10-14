from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.categories import CategoryService
from app.services.products import ProductService
from app.services.reviews import ReviewService

from app.core.dependencies.db import get_async_db
from app.repositories.categories import CategoryRepository
from app.repositories.products import ProductRepository
from app.repositories.reviews import ReviewRepository
from app.repositories.users import UserRepository


def get_category_service(db: AsyncSession = Depends(get_async_db)) -> CategoryService:
    return CategoryService(category_repo=CategoryRepository(db=db))


def get_product_service(db: AsyncSession = Depends(get_async_db)) -> ProductService:
    return ProductService(
        product_repo=ProductRepository(db=db),
        category_repo=CategoryRepository(db=db),
        user_repo=UserRepository(db=db),
    )


def get_review_service(db: AsyncSession = Depends(get_async_db)) -> ReviewService:
    return ReviewService(
        review_repo=ReviewRepository(db=db),
        product_repo=ProductRepository(db=db),
        user_repo=UserRepository(db=db),
    )
