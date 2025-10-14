from typing import Annotated
from fastapi import APIRouter, Depends, status, Path
from pydantic import Field
from app.schemas.products import ProductCreate, Product

from app.core.dependencies.services import get_product_service
from app.services.products import ProductService
from app.auth.security import get_email_current_user


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[Product], status_code=status.HTTP_200_OK)
async def get_products(
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> list[Product]:
    return await product_service.get_all_products()


@router.get("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
async def get_product_by_id(
    product_id: Annotated[int, Path(ge=1)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> Product:
    return await product_service.get_by_id(product_id=product_id)


@router.get(
    "/category/{category_id}",
    response_model=list[Product],
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    category_id: Annotated[int, Path(ge=1)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> list[Product]:
    return await product_service.get_products_by_category(category_id=category_id)


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_create: Annotated[ProductCreate, Field(description="Create product data")],
    product_service: Annotated[ProductService, Depends(get_product_service)],
    user_email: Annotated[str, Depends(get_email_current_user)],
) -> Product:
    return await product_service.create(
        product_create=product_create, email_user=user_email
    )


@router.put("/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
async def product_update(
    product_id: Annotated[int, Path(ge=1)],
    update_product: Annotated[ProductCreate, Field(description="Update product data")],
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> Product:
    return await product_service.update(
        product_id=product_id, product_update=update_product
    )


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def product_delete(
    product_id: Annotated[int, Path(ge=1)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> dict:
    await product_service.delete(product_id=product_id)
    return {"success": "product success deleted"}
