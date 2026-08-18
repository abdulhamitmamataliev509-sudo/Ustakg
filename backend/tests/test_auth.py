"""Auth flow tests: register, login, refresh, /me."""
import secrets

from fastapi.testclient import TestClient


def _phone() -> str:
    return "+9967" + "".join(str(secrets.randbelow(10)) for _ in range(8))


def _register(client: TestClient, phone: str, role: str, full_name: str = "Test User"):
    return client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": phone,
            "password": "secret123",
            "full_name": full_name,
            "role": role,
        },
    )


def test_register_login_refresh_me(client: TestClient):
    phone = _phone()
    reg = _register(client, phone, "CUSTOMER", "Aigul Customer")
    assert reg.status_code == 201, reg.text
    tokens = reg.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["phone_number"] == phone
    assert me.json()["role"] == "CUSTOMER"
    assert me.json()["is_active"] is True

    login = client.post(
        "/api/v1/auth/login",
        data={"username": phone, "password": "secret123"},
    )
    assert login.status_code == 200, login.text
    assert login.json()["access_token"]

    refresh = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh.status_code == 200, refresh.text
    assert refresh.json()["access_token"]


def test_register_master_creates_profile(client: TestClient):
    phone = _phone()
    reg = _register(client, phone, "MASTER", "Usta Master")
    assert reg.status_code == 201, reg.text

    login = client.post(
        "/api/v1/auth/login", data={"username": phone, "password": "secret123"}
    )
    assert login.status_code == 200
    masters = client.get("/api/v1/masters/")
    assert masters.status_code == 200
    assert "Usta Master" in [m["full_name"] for m in masters.json()]


def test_register_duplicate_phone_conflict(client: TestClient):
    phone = _phone()
    first = _register(client, phone, "CUSTOMER")
    second = _register(client, phone, "CUSTOMER")
    assert first.status_code == 201
    assert second.status_code == 409


def test_me_requires_token(client: TestClient):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_login_wrong_password(client: TestClient):
    phone = _phone()
    _register(client, phone, "CUSTOMER")
    r = client.post(
        "/api/v1/auth/login", data={"username": phone, "password": "wrongpass"}
    )
    assert r.status_code == 401


def test_register_invalid_phone_format(client: TestClient):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": "5551234",
            "password": "secret123",
            "full_name": "X",
            "role": "CUSTOMER",
        },
    )
    assert r.status_code == 422


def test_register_admin_role_forbidden(client: TestClient):
    r = _register(client, _phone(), "ADMIN", "Fake Admin")
    assert r.status_code == 403