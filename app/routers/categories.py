from fastapi import APIRouter

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/")
async def get_categories():
    """Возвращает список всех категорий товаров."""
    return {"message": "Список всех категорий (заглушка)"}


@router.post("/")
async def create_category():
    """Создает новую категорию."""
    return {"message": "Категория создана (заглушка)"}


@router.put("/{category_id}")
async def update_category(category_id: int):
    """Обновляет новую категорию по ее ID."""
    return {"message": f"Категория с ID-{category_id} обновленна (заглушка)"}


@router.delete("/{category_id}")
async def delete_category(category_id: int):
    """Удаляет категорию по ее ID."""
    return {"message": f"Категория c ID-{category_id} удаленна (заглушка)"}
