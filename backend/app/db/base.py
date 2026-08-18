"""Central SQLAlchemy Base and model registry.

Import every model here so that Alembic autogenerate can discover all
tables and mappers are configured at startup.
"""
from app.core.database import Base  # noqa: F401
from app.models.category import Category, MasterCategory  # noqa: F401
from app.models.chat import Chat, ChatMessage  # noqa: F401
from app.models.enums import OfferStatus, OrderStatus, UserRole  # noqa: F401
from app.models.master import MasterProfile  # noqa: F401
from app.models.order import Order, OrderOffer  # noqa: F401
from app.models.review import Review  # noqa: F401
from app.models.user import User  # noqa: F401
