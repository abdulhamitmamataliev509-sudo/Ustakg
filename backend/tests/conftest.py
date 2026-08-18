"""Pytest configuration and fixtures.

Creates a dedicated ``ustakg_test_db`` PostgreSQL database and applies the
Alembic migrations (source of truth) before the test session starts. The DB
name is injected via an environment variable set *before* the app package is
imported, so the SQLAlchemy engine binds to the test database.
"""
import os

os.environ["POSTGRES_DB"] = "ustakg_test_db"

import psycopg2  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.main import app  # noqa: E402
from app.models.enums import UserRole  # noqa: E402
from app.models.user import User  # noqa: E402


def _ensure_test_db() -> None:
    """Create ``ustakg_test_db`` if it does not already exist."""
    conn = psycopg2.connect(
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname="postgres",
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.POSTGRES_DB,))
    if cur.fetchone() is None:
        cur.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}"')
    cur.close()
    conn.close()


def _run_migrations() -> None:
    """Apply Alembic migrations up to head on the test database."""
    from alembic import command
    from alembic.config import Config

    cfg = Config("alembic.ini")
    cfg.set_main_option("script_location", "app/db/migrations")
    command.upgrade(cfg, "head")


_ensure_test_db()
_run_migrations()


@pytest.fixture(scope="session")
def client() -> TestClient:
    """A TestClient bound to the migrated test database."""
    return TestClient(app)


@pytest.fixture(scope="session")
def admin_token(client: TestClient) -> str:
    """A valid access token for a seeded ADMIN user."""
    phone = "+996700000001"
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.phone_number == phone).first()
        if user is None:
            user = User(
                phone_number=phone,
                hashed_password=get_password_hash("adminsecret"),
                full_name="Test Admin",
                role=UserRole.ADMIN,
            )
            db.add(user)
            db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/auth/login",
        data={"username": phone, "password": "adminsecret"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]