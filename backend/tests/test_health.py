"""Health-check & analytics tests."""
import logging

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_v1_health_db_and_websocket():
    """Production health endpoint reports DB connectivity and version."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["database"] == "ok"
    assert body["version"] == "1.0.0"
    assert "websocket_rooms" in body


def test_ready_probe():
    """The /ready readiness probe verifies DB connectivity."""
    response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["version"] == "1.0.0"


def test_structured_json_logging(monkeypatch):
    """JsonFormatter serializes records as parseable JSON lines."""
    import json

    from app.core.logging import JsonFormatter

    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="ustakg.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_completed",
        args=None,
        exc_info=None,
    )
    for key, value in (
        ("method", "GET"),
        ("path", "/health"),
        ("status_code", 200),
        ("duration_ms", 1.5),
    ):
        setattr(record, key, value)

    data = json.loads(formatter.format(record))
    assert data["message"] == "request_completed"
    assert data["method"] == "GET"
    assert data["path"] == "/health"
    assert data["status_code"] == 200


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_analytics_track_event(monkeypatch):
    """track_event emits a structured JSON line via the analytics logger."""
    import json

    from app.core.analytics import logger as analytics_logger
    from app.core.analytics import track_event

    captured: dict = {}

    def fake_info(msg: str) -> None:
        captured["msg"] = msg

    monkeypatch.setattr(analytics_logger, "info", fake_info)
    track_event("user.registered", {"user_id": "u1", "role": "CUSTOMER"})

    data = json.loads(captured["msg"])
    assert data["event"] == "user.registered"
    assert data["payload"] == {"user_id": "u1", "role": "CUSTOMER"}
    assert "ts" in data

