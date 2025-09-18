# pylint:disable=unused-argument
# ruff:noqa:E712
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.dependencies.db import get_async_db
from app.auth import get_current_buyer, get_admin
from app.utils.reviews.update_rating import update_rating

router = APIRouter(tags=["reviews"])


@router.get(
    "/reviews", status_code=status.HTTP_200_OK, response_model=list[ReviewSchema]
)
async def get_reviews(db: AsyncSession = Depends(get_async_db)):
    """Получает все активные отзывы"""
    result = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    reviews = result.all()
    return reviews


@router.get(
    "/products/{product_id}/reviews",
    response_model=list[ReviewSchema],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_by_product(
    product_id: Annotated[int, Path(..., ge=1)],
    db: AsyncSession = Depends(get_async_db),
):
    """Получает все активные отзывы о продукте"""
    result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == product_id, ProductModel.is_active == True
        )
    )
    product = result.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id-{product_id} not found",
        )
    result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.product_id == product.id, ReviewModel.is_active == True
        )
    )
    reviews = result.all()
    return reviews


@router.post(
    "/reviews", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED
)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_buyer),
):
    """Создает отзыв"""
    result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == review.product_id, ProductModel.is_active == True
        )
    )
    product = result.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product id not found",
        )
    review_db = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(review_db)
    await db.commit()
    await db.refresh(review_db)
    await update_rating(review_db, db)
    return review_db


@router.delete("/review/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: Annotated[int, Path(..., ge=1)],
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_admin),
):
    """Удаляет отзыв по ID."""
    result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.id == review_id, ReviewModel.is_active == True
        )
    )
    review = result.first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review id not found",
        )

    await db.execute(
        update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False)
    )
    await db.commit()
    await db.refresh(review)
    await update_rating(review, db)
    return {"message": "Review deleted"}
