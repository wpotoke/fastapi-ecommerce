from typing import Annotated
from fastapi import APIRouter, Depends, status, Path
from pydantic import Field
from app.schemas.categories import CategoryCreate, Category

from app.core.dependencies.services import get_category_service
from app.services.categories import CategoryService


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[Category], status_code=status.HTTP_200_OK)
async def get_categories(
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[Category]:
    return await category_service.get_all_categories()


@router.get("/{category_id}", response_model=Category, status_code=status.HTTP_200_OK)
async def get_category(
    category_id: Annotated[int, Path(ge=1)],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> Category:
    return await category_service.get_category_by_id(category_id=category_id)


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: Annotated[CategoryCreate, Field(description="Create category data")],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> Category:
    return await category_service.create_category(category=category)


@router.put("/{category_id}", response_model=Category, status_code=status.HTTP_200_OK)
async def update_category(
    category_id: Annotated[int, Path(ge=1)],
    category: Annotated[CategoryCreate, Field(description="Update category data")],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> Category:
    return await category_service.update_category(
        category_id=category_id, category=category
    )


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: Annotated[int, Path(ge=1)],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> dict:
    res = await category_service.delete_category(category_id=category_id)
    if res:
        return {"success": "Category success deleted"}
    return {"success": "Category not exists"}
