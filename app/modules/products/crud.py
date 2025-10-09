# ruff: noqa: E712
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.modules.products.models import Product as ProductModel
from app.modules.users.models import User as UserModel
from app.modules.products.schemas import ProductCreate


async def crud_get_products(db: AsyncSession):
    """Возвращает список всех товаров."""
    result = await db.scalars(
        select(ProductModel).where(ProductModel.is_active == True)
    )
    products = result.all()
    return products


async def crud_create_product(
    product_create: ProductCreate,
    db: AsyncSession,
    current_user: UserModel,
):
    """Создает новый товар."""
    product = ProductModel(**product_create.model_dump(), seller_id=current_user.id)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def crud_get_products_by_category(
    category_id: int,
    db: AsyncSession,
):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    stmt = select(ProductModel).where(
        ProductModel.category_id == category_id, ProductModel.is_active == True
    )
    result = await db.scalars(stmt)
    products = result.all()
    return products


async def crud_get_product(
    product_id: int,
    db: AsyncSession,
):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    stmt = select(ProductModel).where(
        ProductModel.id == product_id, ProductModel.is_active == True
    )
    result = await db.scalars(stmt)
    product = result.first()
    return product


async def crud_update_product(
    product_id: int,
    product_update: ProductCreate,
    db: AsyncSession,
):
    """Обновляет товар по ID."""
    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product_update.model_dump())
    )
    await db.commit()
    return await crud_get_product(product_id, db)


async def crud_delete_product(
    product_id: int,
    db: AsyncSession,
):
    """Удаляет продукт по ID."""
    result = await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(is_active=False)
    )
    await db.commit()
    return result.rowcount > 0
