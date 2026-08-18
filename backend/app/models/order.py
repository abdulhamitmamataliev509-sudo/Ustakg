"""Order and order-offer models."""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UuidPkMixin, utcnow
from app.models.enums import OfferStatus, OrderStatus


class Order(UuidPkMixin, TimestampMixin, Base):
    """A job/service request posted by a customer."""

    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_status_created", "status", "created_at"),
        Index("ix_orders_category_id", "category_id"),
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("categories.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    location_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    address_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.OPEN, nullable=False
    )

    customer: Mapped["User"] = relationship(
        back_populates="customer_orders", foreign_keys="Order.customer_id"
    )
    category: Mapped["Category"] = relationship()
    offers: Mapped[list["OrderOffer"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    review: Mapped["Review | None"] = relationship(back_populates="order", uselist=False)

    @property
    def category_title(self) -> str:
        return self.category.title


class OrderOffer(UuidPkMixin, Base):
    """A bid/offer submitted by a master for an order."""

    __tablename__ = "order_offers"
    __table_args__ = (
        Index("ix_order_offers_order_id", "order_id"),
        Index("ix_order_offers_master_id", "master_id"),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("orders.id"), nullable=False)
    master_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("master_profiles.id"), nullable=False
    )
    proposed_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[OfferStatus] = mapped_column(
        Enum(OfferStatus), default=OfferStatus.PENDING, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    order: Mapped["Order"] = relationship(back_populates="offers")
    master: Mapped["MasterProfile"] = relationship(back_populates="offers")

    @property
    def master_full_name(self) -> str:
        return self.master.full_name