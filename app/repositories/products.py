# ruff: noqa: E712
# pylint:disable=not-callable
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.schemas.products import ProductCreate
from app.core.exceptions import BusinessException


class ProductRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        page: int,
        page_size: int,
        category_id: int | None,
        rating: float | None,
        min_price: float | None,
        max_price: float | None,
        in_stock: bool | None,
        seller_id: int | None,
    ) -> dict:
        """Возвращает список всех товаров с пагинацией и фильтрацией"""
        if min_price is not None and max_price is not None and min_price > max_price:
            raise BusinessException(
                detail="Минимальная цена не может быть больше максимальной"
            )

        filters = [ProductModel.is_active == True]

        if category_id is not None:
            filters.append(ProductModel.category_id == category_id)
        if rating is not None:
            filters.append(ProductModel.rating >= rating)
        if min_price is not None:
            filters.append(ProductModel.price >= min_price)
        if max_price is not None:
            filters.append(ProductModel.price <= max_price)
        if in_stock is not None:
            filters.append(
                ProductModel.stock > 0 if in_stock else ProductModel.stock == 0
            )
        if seller_id is not None:
            filters.append(ProductModel.seller_id == seller_id)

        result = await self.db.scalar(
            select(func.count()).select_from(ProductModel).where(*filters)
        )
        total = int(result or 0)
        products_stmt = await self.db.scalars(
            select(ProductModel)
            .where(*filters)
            .order_by(ProductModel.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        products = products_stmt.all()
        return {"items": products, "total": total, "page": page, "page_size": page_size}

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
