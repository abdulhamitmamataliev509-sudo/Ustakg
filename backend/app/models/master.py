"""Service-master profile model."""
import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UuidPkMixin


class MasterProfile(UuidPkMixin, Base):
    """Extended profile attached to a user with the MASTER role."""

    __tablename__ = "master_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), unique=True, nullable=False
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passport_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="master_profile")
    categories: Mapped[list["Category"]] = relationship(
        secondary="master_categories", back_populates="masters"
    )
    reviews: Mapped[list["Review"]] = relationship(back_populates="master")
    offers: Mapped[list["OrderOffer"]] = relationship(back_populates="master")

    @property
    def full_name(self) -> str:
        return self.user.full_name

    @property
    def phone_number(self) -> str:
        return self.user.phone_number

    @property
    def avatar_url(self) -> str | None:
        return self.user.avatar_url