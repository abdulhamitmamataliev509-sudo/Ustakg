"""Category endpoint tests: public listing + admin-only creation."""
import secrets

from fastapi.testclient import TestClient


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_list_categories_public(client: TestClient):
    response = client.get("/api/v1/categories/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_and_list_categories(client: TestClient, admin_token: str):
    headers = _auth(admin_token)
    slug = f"electrical-{secrets.token_hex(3)}"

    root = client.post(
        "/api/v1/categories/",
        headers=headers,
        json={"title": "Электромонтаж", "slug": slug},
    )
    assert root.status_code == 201, root.text
    root_id = root.json()["id"]

    child = client.post(
        "/api/v1/categories/",
        headers=headers,
        json={"title": "Розетки", "slug": f"sockets-{slug}", "parent_id": root_id},
    )
    assert child.status_code == 201, child.text

    listing = client.get("/api/v1/categories/")
    assert listing.status_code == 200
    roots = [c for c in listing.json() if c["slug"] == slug]
    assert len(roots) == 1
    assert len(roots[0]["children"]) == 1
    assert roots[0]["children"][0]["slug"] == f"sockets-{slug}"


def test_create_category_forbidden_for_customer(client: TestClient):
    phone = "+9967" + "".join(str(secrets.randbelow(10)) for _ in range(8))
    client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": phone,
            "password": "secret123",
            "full_name": "Cust",
            "role": "CUSTOMER",
        },
    )
    login = client.post(
        "/api/v1/auth/login", data={"username": phone, "password": "secret123"}
    )
    headers = _auth(login.json()["access_token"])
    r = client.post(
        "/api/v1/categories/",
        headers=headers,
        json={"title": "Нет", "slug": "no-access"},
    )
    assert r.status_code == 403