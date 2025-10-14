# ruff: noqa: E712
from typing import Optional
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import Review as ReviewModel
from app.models.users import User as UserModel
from app.schemas.reviews import ReviewCreate
from app.models.products import Product as ProductModel


class ReviewRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[ReviewModel]:
        """Получает все активные отзывы"""
        result = await self.db.scalars(
            select(ReviewModel).where(ReviewModel.is_active == True)
        )
        reviews = result.all()
        return reviews

    async def get_by_id(self, review_id: int) -> Optional[ReviewModel]:
        result = await self.db.scalars(
            select(ReviewModel).where(
                ReviewModel.id == review_id, ReviewModel.is_active == True
            )
        )
        review = result.first()
        return review

    async def get_reviews_by_product(
        self,
        product_id: int,
    ) -> list[ReviewModel]:
        """Получает все активные отзывы о продукте"""
        result = await self.db.scalars(
            select(ReviewModel).where(
                ReviewModel.product_id == product_id, ReviewModel.is_active == True
            )
        )
        reviews = result.all()
        return reviews

    async def create(
        self,
        review: ReviewCreate,
        current_user: UserModel,
    ) -> Optional[ReviewModel]:
        """Создает отзыв"""
        review_db = ReviewModel(**review.model_dump(), user_id=current_user.id)
        self.db.add(review_db)
        await self.db.commit()
        await self.db.refresh(review_db)
        return review_db

    async def update(self, review_id: int, review_update: ReviewCreate):
        result = await self.db.execute(
            update(ReviewModel)
            .where(ReviewModel.id == review_id, ReviewModel.is_active == True)
            .values(**review_update.model_dump())
        )
        await self.db.commit()
        if result.rowcount > 0:
            return await self.get_by_id(review_id)
        return None

    async def delete(
        self,
        review_id: int,
    ) -> bool:
        """Удаляет отзыв по ID."""
        result = await self.db.execute(
            update(ReviewModel)
            .where(ReviewModel.id == review_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def check_existing(self, user_id: int, product_id: int):
        review = await self.db.scalars(
            select(ReviewModel).where(
                ReviewModel.user_id == user_id,
                ReviewModel.product_id == product_id,
                ReviewModel.is_active == True,
            )
        )
        return review.first()

    async def update_rating(self, review: ReviewModel):
        result = await self.db.scalars(
            select(func.avg(ReviewModel.grade)).where(
                ReviewModel.product_id == review.product_id,
                ReviewModel.is_active == True,
            )
        )
        await self.db.execute(update(ProductModel).values(rating=result.first()))
        await self.db.commit()
        await self.db.refresh(review)
