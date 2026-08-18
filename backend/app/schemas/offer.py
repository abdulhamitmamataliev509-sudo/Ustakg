"""Order-offer schemas."""
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OfferStatus


class OfferCreate(BaseModel):
    order_id: uuid.UUID
    proposed_price: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    comment: str | None = Field(default=None, max_length=1000)


class OfferOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    master_id: uuid.UUID
    master_full_name: str
    proposed_price: Decimal
    comment: str | None = None
    status: OfferStatus
    created_at: datetime
