"""Production health check endpoint.

Returns DB connectivity status, WebSocket manager readiness, and version.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.websocket import manager

router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)):
    """Return basic system health information.

    - db: attempts a lightweight `SELECT 1` to ensure connectivity
    - websocket_manager: reports number of active chat rooms
    - version: static application version
    """
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    ws_rooms = len(manager.active)

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "down",
        "websocket_rooms": ws_rooms,
        "version": "1.0.0",
    }
