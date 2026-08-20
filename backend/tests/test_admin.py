"""Admin endpoint tests: stats, user list, verify, block."""
import secrets
import uuid

from fastapi.testclient import TestClient


def _register(client: TestClient, role: str = "CUSTOMER") -> dict:
    phone = "+9967" + "".join(str(secrets.randbelow(10)) for _ in range(8))
    r = client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": phone,
            "password": "secret123",
            "full_name": f"Test {secrets.token_hex(3)}",
            "role": role,
        },
    )
    assert r.status_code == 201, r.text
    return {"phone": phone, **r.json()}


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_admin_stats_ok(client, admin_token):
    res = client.get("/api/v1/admin/stats", headers=_auth(admin_token))
    assert res.status_code == 200
    body = res.json()
    assert body["total_users"] >= 0
    assert body["total_masters"] >= 0
    assert body["open_orders"] >= 0
    assert body["system_status"] == "ok"


def test_admin_stats_forbidden_for_customer(client):
    acc = _register(client, "CUSTOMER")
    res = client.get("/api/v1/admin/stats", headers=_auth(acc["access_token"]))
    assert res.status_code == 403


def test_admin_stats_requires_auth(client):
    assert client.get("/api/v1/admin/stats").status_code == 401


def test_admin_list_users(client, admin_token):
    _register(client, "MASTER")
    res = client.get("/api/v1/users/", headers=_auth(admin_token))
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1


def test_admin_block_and_verify(client, admin_token):
    acc = _register(client, "MASTER")
    me = client.get("/api/v1/auth/me", headers=_auth(acc["access_token"]))
    assert me.status_code == 200
    uid = me.json()["id"]

    block = client.post(f"/api/v1/users/{uid}/block", headers=_auth(admin_token))
    assert block.status_code == 200
    assert block.json()["is_active"] is False

    verify = client.post(f"/api/v1/users/{uid}/verify", headers=_auth(admin_token))
    assert verify.status_code == 200
    assert verify.json()["is_verified"] is True


def test_admin_user_ops_forbidden_for_customer(client):
    acc = _register(client, "CUSTOMER")
    me = client.get("/api/v1/auth/me", headers=_auth(acc["access_token"]))
    uid = me.json()["id"]
    res = client.post(f"/api/v1/users/{uid}/block", headers=_auth(acc["access_token"]))
    assert res.status_code == 403


def test_admin_user_ops_404(client, admin_token):
    res = client.post(f"/api/v1/users/{uuid.uuid4()}/block", headers=_auth(admin_token))
    assert res.status_code == 404