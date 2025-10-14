# pylint:disable=unused-argument
# ruff:noqa:E712
from typing import Annotated
from fastapi import APIRouter, Depends, status, Path
from pydantic import Field
from app.core.dependencies.services import get_review_service
from app.services.reviews import ReviewService
from app.schemas.reviews import Review, ReviewCreate
from app.auth.security import get_email_current_user

router = APIRouter(tags=["reviews"])


@router.get("/reviews", status_code=status.HTTP_200_OK, response_model=list[Review])
async def get_reviews(
    review_repo: ReviewService = Depends(get_review_service),
) -> list[Review]:
    return await review_repo.get_all_reviews()


@router.get(
    "/products/{product_id}/reviews",
    response_model=list[Review],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_by_product(
    product_id: Annotated[int, Path(..., ge=1)],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> list[Review]:
    return await review_service.get_reviews_by_product(product_id=product_id)


@router.post("/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: Annotated[ReviewCreate, Field(description="Create review data")],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    email: Annotated[str, Depends(get_email_current_user)],
) -> Review:
    return await review_service.create_review(review=review, email_user=email)


@router.put(
    "/reviews/{review_id}", response_model=Review, status_code=status.HTTP_200_OK
)
async def update_review(
    review_id: Annotated[int, Path(..., ge=1)],
    review: Annotated[ReviewCreate, Field(description="Create review data")],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    email: Annotated[str, Depends(get_email_current_user)],
) -> Review:
    return await review_service.update_review(
        review_id=review_id, review=review, email_user=email
    )


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_review(
    review_id: Annotated[int, Path(..., ge=1)],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    email: Annotated[str, Depends(get_email_current_user)],
) -> dict:
    result = await review_service.delete_review(review_id=review_id, email_user=email)
    if result:
        return {"success": "review success deleted"}
    return {"error": "review wont delete"}
