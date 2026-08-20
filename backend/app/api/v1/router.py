"""Aggregate all version-1 API endpoint routers."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    categories,
    chats,
    health,
    masters,
    offers,
    orders,
    reviews,
    users,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(masters.router, prefix="/masters", tags=["masters"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(offers.router, prefix="/offers", tags=["offers"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(health.router, prefix="", tags=["health"])
