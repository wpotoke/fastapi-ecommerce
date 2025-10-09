# pylint:disable=unused-argument
# ruff:noqa:E712
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User as UserModel
from app.modules.reviews.schemas import Review as ReviewSchema, ReviewCreate
from app.core.dependencies import get_async_db
from app.modules.users.auth import get_current_buyer, get_current_user
from app.modules.reviews.utils import update_rating
from app.modules.reviews.crud import (
    crud_create_review,
    crud_delete_review,
    crud_get_review,
    crud_get_reviews,
    crud_get_reviews_by_product,
    crud_check_existing_review,
)
from app.modules.products.crud import crud_get_product

router = APIRouter(tags=["reviews"])


@router.get(
    "/reviews", status_code=status.HTTP_200_OK, response_model=list[ReviewSchema]
)
async def get_reviews(db: Annotated[AsyncSession, Depends(get_async_db)]):
    """Получает все активные отзывы"""
    reviews_db = await crud_get_reviews(db)
    return reviews_db


@router.get(
    "/products/{product_id}/reviews",
    response_model=list[ReviewSchema],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_by_product(
    product_id: Annotated[int, Path(..., ge=1)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    """Получает все активные отзывы о продукте"""
    product = await crud_get_product(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id-{product_id} not found",
        )
    reviews_db = await crud_get_reviews_by_product(product.id, db)
    return reviews_db


@router.post(
    "/reviews", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED
)
async def create_review(
    review: ReviewCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: UserModel = Depends(get_current_buyer),
):
    """Создает отзыв"""
    product = await crud_get_product(review.product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product id not found",
        )
    existing_review = await crud_check_existing_review(product.id, current_user.id, db)
    if existing_review:
        raise HTTPException(400, detail="You have already reviewed this product")
    review_db = await crud_create_review(review, db, current_user)
    await update_rating(review_db, db)
    return review_db


@router.delete(
    "/review/{review_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_review(
    review_id: Annotated[int, Path(..., ge=1)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Удаляет отзыв по ID."""
    review = await crud_get_review(review_id, db)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review id not found",
        )

    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews",
        )

    success = await crud_delete_review(review_id, db)
    if success:
        await update_rating(review, db)
        return {"message": "Review deleted"}
    return {"message": "Failed to delete review"}


#  Проверить как работает depenedencies в delete_review !!!!!!!!!!!
