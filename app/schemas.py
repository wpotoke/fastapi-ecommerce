from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class CategoryCreate(BaseModel):
    """Модель для создания и обновления категории.
    Используеться для POST и PUT запросах."""

    name: Annotated[
        str, Field(min_length=3, max_length=50, description="Название категории")
    ]
    parent_id: Annotated[
        int | None, Field(None, description="ID родительской категории, если есть")
    ]


class Category(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    """

    id: Annotated[int, Field(description="Уникальный инентификатор категории")]
    name: Annotated[str, Field(description="Название категории")]
    parent_id: Annotated[
        int | None, Field(None, description="ID родительской категории, если есть")
    ]
    is_active: Annotated[bool, Field(description="Активность категории")]

    model_config = ConfigDict(from_attributes=True)


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
    stock: Annotated[int, Field(ge=0, description="Колличество товара на складе")]
    category_id: Annotated[
        int, Field(description="ID категории, к которой относится товар")
    ]
    is_active: Annotated[bool, Field(description="Активность товара")]

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: Annotated[EmailStr, Field(description="Email пользователя")]
    password: Annotated[
        str, Field(min_length=8, description="Пароль (минимум 8 символов)")
    ]
    role: Annotated[
        str,
        Field(
            default="buyer",
            pattern="^(buyer|seller)$",
            description="Роль: 'buyer' или 'seller'",
        ),
    ]


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)
