from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
async def get_products():
    """Возвращает список всех товаров."""
    return {"message": "Список всех (заглушка)"}


@router.post("/")
async def create_product():
    """Создает новый товар."""
    return {"message": "Товар создан (заглушка)"}


@router.get("/category/{category_id}")
async def get_products_by_category(category_id):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    return {"message": f"Товары в категории {category_id} (заглушка)"}


@router.get("/{product_id}")
async def get_product(product_id: int):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    return {"message": f"Детали товара {product_id} (заглушка)"}


@router.put("/{product_id}")
async def update_product(product_id: int):
    """Обновляет товар по ID."""
    return {"message": f"Товар с ID-{product_id} обновлен (заглушка)"}


@router.delete("/{product_id}")
async def delete_category(product_id: int):
    """Удаляет категорию по ее ID."""
    return {"message": f"Товар c ID-{product_id} удален (заглушка)"}
