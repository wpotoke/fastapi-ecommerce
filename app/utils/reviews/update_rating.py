# ruff:noqa:E712
# pylint:disable=import-error
from fastapi import Depends
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.db import get_async_db
from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel


async def update_rating(review: ReviewModel, db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == review.product_id, ReviewModel.is_active == True
        )
    )
    await db.execute(update(ProductModel).values(rating=result.first()))
    await db.commit()
    await db.refresh(review)
