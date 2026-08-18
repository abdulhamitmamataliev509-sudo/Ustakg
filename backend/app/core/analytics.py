"""Simple analytics / audit event logger.

This module provides a lightweight helper to emit structured audit events
to the application logs. In production you can replace the implementation
to forward events to a metrics/analytics backend (e.g., Prometheus, Segment,
or a message queue).
"""
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("ustakg.analytics")


def track_event(event: str, payload: dict | None = None) -> None:
    """Emit a structured analytics event to the application log.

    event: short name like 'user.register', 'order.created', etc.
    payload: dict with additional dimensions (user_id, order_id, role)
    """
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "payload": payload or {},
    }
    # Log at INFO level; log aggregator should capture these lines.
    logger.info(json.dumps(record))
