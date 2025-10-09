# ruff: noqa: E712
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reviews.models import Review as ReviewModel
from app.modules.users.models import User as UserModel
from app.modules.reviews.schemas import ReviewCreate


async def crud_get_reviews(db: AsyncSession):
    """Получает все активные отзывы"""
    result = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    reviews = result.all()
    return reviews


async def crud_get_review(review_id: int, db: AsyncSession):
    result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.id == review_id, ReviewModel.is_active == True
        )
    )
    review = result.first()
    return review


async def crud_get_reviews_by_product(
    product_id: int,
    db: AsyncSession,
):
    """Получает все активные отзывы о продукте"""
    result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.product_id == product_id, ReviewModel.is_active == True
        )
    )
    reviews = result.all()
    return reviews


async def crud_create_review(
    review: ReviewCreate,
    db: AsyncSession,
    current_user: UserModel,
):
    """Создает отзыв"""
    review_db = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(review_db)
    await db.commit()
    await db.refresh(review_db)
    return review_db


async def crud_delete_review(
    review_id: int,
    db: AsyncSession,
):
    """Удаляет отзыв по ID."""

    result = await db.execute(
        update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False)
    )
    await db.commit()
    return result.rowcount > 0


async def crud_check_existing_review(user_id: int, product_id: int, db: AsyncSession):
    review = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.user_id == user_id,
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True,
        )
    )
    return review.first()
