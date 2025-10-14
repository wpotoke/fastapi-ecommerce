# ruff: noqa: E712
from typing import Optional
from app.schemas.reviews import ReviewCreate
from app.models.reviews import Review as ReviewModel
from app.repositories.reviews import ReviewRepository
from app.repositories.products import ProductRepository
from app.repositories.users import UserRepository
from app.core.exceptions import NotFoundException, ConflictException, BusinessException


class ReviewService:

    def __init__(
        self,
        review_repo: ReviewRepository,
        product_repo: ProductRepository,
        user_repo: UserRepository,
    ):
        self.review_repo = review_repo
        self.product_repo = product_repo
        self.user_repo = user_repo

    async def get_all_reviews(self) -> list[ReviewModel]:
        reviews_db = await self.review_repo.get_all()
        return reviews_db

    async def get_review_by_id(self, review_id: int) -> Optional[ReviewModel]:
        review_db = await self.review_repo.get_by_id(review_id)
        if not review_db:
            raise NotFoundException(f"Review with id {review_id} not found")
        return review_db

    async def get_reviews_by_product(self, product_id: int) -> list[ReviewModel]:
        review_db = await self.review_repo.get_reviews_by_product(product_id)
        return review_db

    async def create_review(
        self,
        review: ReviewCreate,
        email_user: str,
    ):
        product = await self.product_repo.get_by_id(review.product_id)
        if not product:
            raise NotFoundException(
                f"Review with product id {review.product_id} not found"
            )
        current_user = await self.user_repo.get_user_by_email(email=email_user)
        if not current_user:
            raise NotFoundException("User with this email not found")
        if current_user.role not in ("seller", "admin"):
            raise BusinessException("Action not allowed for this user role")
        existing_review = await self.review_repo.check_existing(
            product.id, current_user.id
        )
        if existing_review:
            raise ConflictException("Review already existing")
        review_db = await self.review_repo.create(review, current_user)
        await self.review_repo.update_rating(review_db)
        return review_db

    async def update_review(self, review_id, review: ReviewCreate, email_user: str):
        review_db = await self.review_repo.get_by_id(review_id)
        if not review_db:
            raise NotFoundException(f"Review with id {review_id} not found")
        product = await self.product_repo.get_by_id(review.product_id)
        if not product:
            raise NotFoundException(
                f"Review with product id {review.product_id} not found"
            )
        current_user = await self.user_repo.get_user_by_email(email_user)
        if not current_user:
            raise NotFoundException("User with this email for found")
        if current_user.id != review_db.user_id and current_user.role != "admin":
            raise BusinessException(detail="Action not allowed", status_code=403)
        review_upt_db = await self.review_repo.update(
            review_id,
            review,
        )
        await self.review_repo.update_rating(review_upt_db)
        return review_upt_db

    async def delete_review(self, review_id: int, email_user: str):
        review_db = await self.review_repo.get_by_id(review_id)
        if not review_db:
            raise NotFoundException(f"Review with id {review_id} not found")
        current_user = await self.user_repo.get_user_by_email(email_user)
        if not current_user:
            raise NotFoundException("User with this email for found")
        if current_user.id != review_db.user_id and current_user.role != "admin":
            raise BusinessException("Action not allowed", status_code=403)
        review_del_db = await self.review_repo.delete(review_id)
        return review_del_db
