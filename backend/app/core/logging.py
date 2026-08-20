"""Production-ready structured logging and request middleware.

This module provides:

- ``JsonFormatter``: serializes every log record as a single-line JSON object
  so aggregators (ELK, Datadog, CloudWatch, etc.) can parse it uniformly.
- ``configure_logging``: attaches a JSON ``StreamHandler`` to the root logger.
- ``RequestLoggingMiddleware``: emits a structured JSON line for every HTTP
  request/response (method, path, status, latency, client IP, request id).

The ``ustakg.analytics`` logger (see ``app.core.analytics``) continues to emit
business-event JSON lines independently of this access log.
"""
import json
import logging
import sys
import time
from typing import Any, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Fields copied from ``logging.extra`` onto the record, when present.
_EXTRA_FIELDS = (
    "method",
    "path",
    "status_code",
    "duration_ms",
    "request_id",
    "client_ip",
)


class JsonFormatter(logging.Formatter):
    """Serialize log records as single-line JSON.

    Example output::

        {"ts": "2026-08-20T12:00:00+0000", "level": "INFO",
         "logger": "ustakg.access", "message": "request_completed",
         "method": "GET", "path": "/health", "status_code": 200,
         "duration_ms": 2.31, "request_id": "-", "client_ip": "127.0.0.1"}
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in _EXTRA_FIELDS:
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: int = logging.INFO) -> None:
    """Attach a console ``StreamHandler`` using a JSON formatter to the root logger.

    Idempotent: running it more than once (e.g. under ``--reload``) does not
    duplicate handlers. The root level is raised so ``uvicorn`` and third-party
    loggers inherit the JSON formatter and the desired verbosity.
    """
    root = logging.getLogger()
    if any(getattr(h, "_ustakg_json", False) for h in root.handlers):
        return
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler._ustakg_json = True  # type: ignore[attr-defined]
    root.addHandler(handler)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Emit a structured JSON access-log line for every request/response."""

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self._logger = logging.getLogger("ustakg.access")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        request_id = request.headers.get("x-request-id", "-")
        client_ip = request.client.host if request.client else "-"

        try:
            response = await call_next(request)
        except Exception:
            self._logger.exception(
                "unhandled_exception",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": client_ip,
                    "request_id": request_id,
                },
            )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
                "request_id": request_id,
            },
        )
        return response