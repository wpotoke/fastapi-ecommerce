from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    """Модель для создания и обновления продукта.
    Используется в POST и PUT запросах."""

    name: Annotated[
        str, Field(min_length=3, max_length=100, description="Название товара")
    ]
    description: Annotated[
        str | None, Field(None, max_length=500, description="Описание товара")
    ]
    price: Annotated[float | None, Field(None, gt=0, description="Цена товара")]
    image_url: Annotated[
        str | None, Field(None, max_length=200, description="URL изображения товара")
    ]
    stock: Annotated[int, Field(ge=0, description="Колличество товара на складе")]
    category_id: Annotated[
        int, Field(description="ID категории, к которой относится товар")
    ]


class Product(BaseModel):
    """Модель для ответа с данными запроса.
    Используется в GET-запросах."""

    id: Annotated[int, Field(description="Уникальный инентификатор товара")]
    name: Annotated[
        str, Field(min_length=3, max_length=100, description="Название товара")
    ]
    description: Annotated[
        str | None, Field(None, max_length=500, description="Описание товара")
    ]
    price: Annotated[float | None, Field(None, gt=0, description="Цена товара")]
    image_url: Annotated[
        str | None, Field(None, max_length=200, description="URL изображения товара")
    ]
    rating: Annotated[float, Field(description="Рейтинг отзывов о товаре")]
    stock: Annotated[int, Field(ge=0, description="Колличество товара на складе")]
    category_id: Annotated[
        int, Field(description="ID категории, к которой относится товар")
    ]
    is_active: Annotated[bool, Field(description="Активность товара")]

    model_config = ConfigDict(from_attributes=True)
