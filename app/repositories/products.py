# ruff: noqa: E712
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.schemas.products import ProductCreate


class ProductRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[ProductModel]:
        """Возвращает список всех товаров."""
        result = await self.db.scalars(
            select(ProductModel).where(ProductModel.is_active == True)
        )
        products = result.all()
        return products

    async def create(
        self,
        product_create: ProductCreate,
        current_user: UserModel,
    ) -> ProductModel:
        """Создает новый товар."""
        product = ProductModel(**product_create.model_dump(), seller_id=current_user.id)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_by_category(
        self,
        category_id: int,
    ) -> list[ProductModel]:
        """
        Возвращает список товаров в указанной категории по её ID.
        """
        stmt = select(ProductModel).where(
            ProductModel.category_id == category_id, ProductModel.is_active == True
        )
        result = await self.db.scalars(stmt)
        products = result.all()
        return products

    async def get_by_id(
        self,
        product_id: int,
    ) -> Optional[ProductModel]:
        """
        Возвращает детальную информацию о товаре по его ID.
        """
        stmt = select(ProductModel).where(
            ProductModel.id == product_id, ProductModel.is_active == True
        )
        result = await self.db.scalars(stmt)
        product = result.first()
        return product

    async def get_by_name(self, name: str):
        result = await self.db.scalars(
            select(ProductModel.name == name, ProductModel.is_active == True)
        )
        product = result.first()
        return product

    async def update(
        self,
        product_id: int,
        product_update: ProductCreate,
    ) -> Optional[ProductModel]:
        """Обновляет товар по ID."""
        result = await self.db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(**product_update.model_dump())
        )
        await self.db.commit()
        if result.rowcount > 0:
            return await self.get_by_id(product_id)
        return None

    async def delete(
        self,
        product_id: int,
    ) -> bool:
        """Удаляет продукт по ID."""
        result = await self.db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0
