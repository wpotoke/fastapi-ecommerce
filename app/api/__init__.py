from app.api.routers.categories import router as category_router
from app.api.routers.products import router as product_router
from app.api.routers.reviews import router as review_router
from app.api.routers.users import router as user_router

__all__ = ["category_router", "product_router", "review_router", "user_router"]
