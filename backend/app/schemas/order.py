"""Order schemas."""
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OrderStatus
from app.schemas.offer import OfferOut


class OrderCreate(BaseModel):
    category_id: uuid.UUID
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=3)
    budget: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    location_lat: float | None = Field(default=None, ge=-90, le=90)
    location_lng: float | None = Field(default=None, ge=-180, le=180)
    address_text: str | None = Field(default=None, max_length=255)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_id: uuid.UUID
    category_id: uuid.UUID
    category_title: str
    title: str
    description: str
    budget: Decimal | None = None
    location_lat: float | None = None
    location_lng: float | None = None
    address_text: str | None = None
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class OrderDetail(OrderOut):
    offers: list[OfferOut] = []
