from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator


class CategoryCreate(BaseModel):
    """Модель для создания и обновления категории.
    Используеться для POST и PUT запросах."""

    name: Annotated[
        str, Field(min_length=3, max_length=50, description="Название категории")
    ]
    parent_id: Annotated[
        int | None, Field(None, description="ID родительской категории, если есть")
    ]

    @field_validator("parent_id")
    @classmethod
    def validate_parent(cls, value):
        if value == 0:
            return None
        return value


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
