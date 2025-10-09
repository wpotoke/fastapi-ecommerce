from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    product_id: Annotated[
        int, Field(description="ID продукта к которому относится отзыв")
    ]
    comment: Annotated[str, Field(description="Коментарий к отзыву")]
    grade: Annotated[int, Field(ge=1, le=5, description="Оценка")]


class Review(BaseModel):
    id: Annotated[int, Field(description="Уникальный инентификатор товара")]
    user_id: Annotated[int, Field(description="ID пользователя который написал отзыв")]
    product_id: Annotated[
        int, Field(description="ID продукта к которому относится отзыв")
    ]
    comment: Annotated[
        str | None, Field(default=None, description="Коментарий к отзыву")
    ]
    comment_date: Annotated[datetime, Field(description="Дата и время")]
    grade: Annotated[int, Field(ge=1, le=5, description="Оценка")]
    is_active: Annotated[bool, Field(description="Активность отзыва")]

    model_config = ConfigDict(from_attributes=True)
