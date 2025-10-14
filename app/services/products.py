# ruff: noqa: E712
from typing import Optional

from app.models.products import Product as ProductModel
from app.schemas.products import ProductCreate
from app.repositories.products import ProductRepository
from app.repositories.categories import CategoryRepository
from app.repositories.users import UserRepository
from app.core.exceptions import NotFoundException, ConflictException, BusinessException


class ProductService:

    def __init__(
        self,
        product_repo: ProductRepository,
        category_repo: CategoryRepository,
        user_repo: UserRepository,
    ):
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.user_repo = user_repo

    async def get_all_products(self) -> list[ProductModel]:
        products_db = await self.product_repo.get_all()
        return products_db

    async def create(
        self,
        product_create: ProductCreate,
        email_user: str,
    ) -> ProductModel:
        existing_product = await self.product_repo.get_by_name(product_create.name)
        if existing_product:
            raise ConflictException(f"Product '{product_create.name}' already exists")
        product = await self.product_repo.get_by_name(product_create.name)
        if product:
            raise ConflictException(
                f"Product with name {product_create.name} already exists"
            )
        if not product_create.category_id:
            raise BusinessException("Product must have category")
        category = await self.category_repo.get_by_id(product_create.category_id)
        if not category:
            raise NotFoundException(
                f"Product with category id {product_create.category_id} not found"
            )
        current_user = await self.user_repo.get_user_by_email(email_user)
        if not current_user:
            raise NotFoundException("You must login")
        if current_user.role not in ("seller", "admin"):
            raise BusinessException("Action not allowed for this user role")
        return await self.product_repo.create(product_create, current_user)

    async def get_products_by_category(
        self,
        category_id: int,
    ) -> list[ProductModel]:
        products_db = await self.product_repo.get_by_category(category_id)
        if not products_db:
            raise NotFoundException(f"Product with category id {category_id} not found")
        return products_db

    async def get_by_id(
        self,
        product_id: int,
    ) -> Optional[ProductModel]:
        product_db = await self.product_repo.get_by_id(product_id)
        if not product_db:
            raise NotFoundException(f"Product with id {product_id} not found")
        return product_db

    async def update(
        self,
        product_id: int,
        product_update: ProductCreate,
    ) -> Optional[ProductModel]:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException(f"Product with id {product_id} not found")
        if product_update.name != product.name:
            existing_product = await self.product_repo.get_by_name(product_update.name)
            if existing_product:
                raise ConflictException(
                    f"Product '{product_update.name}' already exists"
                )
        if not product_update.category_id:
            raise BusinessException("Product must have category")
        category_id = await self.category_repo.get_by_id(product_update.category_id)
        if not category_id:
            raise NotFoundException(
                f"Product with category id {product_update.category_id} not found"
            )
        return await self.product_repo.update(product_id, product_update)

    async def delete(
        self,
        product_id: int,
    ) -> bool:
        product_existing = await self.product_repo.get_by_id(product_id)
        if not product_existing:
            raise NotFoundException(f"Product with id {product_id} not found")
        return await self.product_repo.delete(product_id)
