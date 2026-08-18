"""Service category schemas."""
import uuid

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    slug: str = Field(..., min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    icon_name: str | None = Field(default=None, max_length=100)
    parent_id: uuid.UUID | None = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    icon_name: str | None = None
    parent_id: uuid.UUID | None = None
    children: list["CategoryOut"] = []
