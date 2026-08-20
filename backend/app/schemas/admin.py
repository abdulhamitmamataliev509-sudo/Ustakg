"""Admin dashboard & user-management response schemas."""
import uuid

from pydantic import BaseModel


class AdminStats(BaseModel):
    total_users: int
    total_masters: int
    open_orders: int
    system_status: str


class UserActionOut(BaseModel):
    status: str
    user_id: uuid.UUID
    is_active: bool | None = None
    is_verified: bool | None = None