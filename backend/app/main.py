"""Usta kg — FastAPI application entrypoint."""
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import RequestLoggingMiddleware, configure_logging

configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Structured JSON request/response access logging
app.add_middleware(RequestLoggingMiddleware)

# CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Versioned API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Liveness probe — returns 200 whenever the process is up.

    Intended for load balancers / uptime monitors. It does not touch the
    database; use ``/ready`` for a dependency-aware readiness check.
    """
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/ready", tags=["health"])
def ready_check(db: Session = Depends(get_db)) -> dict:
    """Readiness probe — verifies connectivity to critical dependencies.

    Attempts a lightweight ``SELECT 1`` against PostgreSQL and reports the
    application version. Consumers (proxies, container orchestration) can use
    this to confirm the service is truly ready to serve traffic.
    """
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "down",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["root"])
def root() -> dict:
    """Root endpoint with a welcome message."""
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API"}
