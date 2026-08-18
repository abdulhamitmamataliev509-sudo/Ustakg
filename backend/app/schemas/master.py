"""Master profile schemas."""
import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryOut


class MasterProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    phone_number: str
    avatar_url: str | None = None
    bio: str | None = None
    experience_years: int
    is_verified: bool
    rating: float
    reviews_count: int
    passport_verified: bool
    categories: list[CategoryOut] = []


class MasterProfileUpdate(BaseModel):
    bio: str | None = Field(default=None, max_length=2000)
    experience_years: int | None = Field(default=None, ge=0, le=100)
    avatar_url: str | None = Field(default=None, max_length=500)
    category_ids: list[uuid.UUID] | None = None
