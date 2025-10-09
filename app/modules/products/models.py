# ruff: noqa: F821
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Numeric
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False
    )
    rating: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)
    seller_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    category: Mapped["Category"] = relationship(
        "Category", back_populates="products"
    )  # ignore
    seller: Mapped["User"] = relationship("User", back_populates="products")
    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="product", uselist=True
    )
