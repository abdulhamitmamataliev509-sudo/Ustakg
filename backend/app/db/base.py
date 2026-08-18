"""Central SQLAlchemy Base and model registry.

Import every model here so that Alembic autogenerate can discover all
tables. Phase 3 will populate the ``app.models`` package.
"""
from app.core.database import Base  # noqa: F401

# Phase 3: import concrete models so they register on Base.metadata.
# from app.models.user import User  # noqa: F401
# from app.models.master import Master  # noqa: F401
# ...
