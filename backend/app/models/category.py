"""Service category and master-category association models."""
import uuid

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UuidPkMixin


class Category(UuidPkMixin, Base):
    """A service category, optionally nested (parent_id self-reference)."""

    __tablename__ = "categories"

    title: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    icon_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("categories.id"), nullable=True
    )

    parent: Mapped["Category | None"] = relationship(
        back_populates="children", remote_side="Category.id"
    )
    children: Mapped[list["Category"]] = relationship(
        back_populates="parent", order_by="Category.title"
    )
    masters: Mapped[list["MasterProfile"]] = relationship(
        secondary="master_categories", back_populates="categories"
    )


class MasterCategory(Base):
    """Many-to-many join between master profiles and categories."""

    __tablename__ = "master_categories"

    master_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("master_profiles.id"), primary_key=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("categories.id"), primary_key=True
    )