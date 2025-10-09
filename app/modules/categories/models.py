# ruff: noqa: F821
from typing import Optional
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    products: Mapped[list["Product"]] = relationship(  # ignore ruff
        "Product", back_populates="category", uselist=True
    )
    parent: Mapped[Optional["Category"]] = relationship(
        "Category", back_populates="children", remote_side="Category.id"
    )
    children: Mapped[list["Category"]] = relationship(
        "Category", back_populates="parent"
    )
