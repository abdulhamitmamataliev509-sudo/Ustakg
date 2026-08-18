"""Shared SQLAlchemy enum types."""
import enum


class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    MASTER = "MASTER"
    ADMIN = "ADMIN"


class OrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class OfferStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"