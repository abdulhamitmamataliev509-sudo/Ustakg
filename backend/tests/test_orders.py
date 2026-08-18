"""Order endpoint tests: creation, listing, details, and status changes."""
import secrets

from fastapi.testclient import TestClient


def _phone() -> str:
    return "+9967" + "".join(str(secrets.randbelow(10)) for _ in range(8))


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_category(client: TestClient, admin_token: str) -> str:
    headers = _auth(admin_token)
    slug = f"cat-{secrets.token_hex(4)}"
    r = client.post(
        "/api/v1/categories/",
        headers=headers,
        json={"title": f"Категория {slug}", "slug": slug},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _register_customer(client: TestClient) -> dict:
    phone = _phone()
    client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": phone,
            "password": "secret123",
            "full_name": "Customer",
            "role": "CUSTOMER",
        },
    )
    login = client.post(
        "/api/v1/auth/login", data={"username": phone, "password": "secret123"}
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _create_order(client: TestClient, headers: dict, category_id: str) -> dict:
    response = client.post(
        "/api/v1/orders/",
        headers=headers,
        json={
            "category_id": category_id,
            "title": "Починить розетку",
            "description": "Замена розетки на кухне",
            "budget": "1500.00",
            "address_text": "Бишкек, ул. Киевская 12",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_list_get_order(client: TestClient, admin_token: str):
    category_id = _create_category(client, admin_token)
    headers = _register_customer(client)

    order = _create_order(client, headers, category_id)
    order_id = order["id"]
    assert order["status"] == "OPEN"
    assert order["category_title"]
    assert str(order["budget"]) == "1500.00"

    listing = client.get("/api/v1/orders/")
    assert listing.status_code == 200
    open_ids = [o["id"] for o in listing.json() if o["status"] == "OPEN"]
    assert order_id in open_ids

    detail = client.get(f"/api/v1/orders/{order_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["title"] == "Починить розетку"


def test_order_status_change_and_authorization(
    client: TestClient, admin_token: str
):
    category_id = _create_category(client, admin_token)
    owner_headers = _register_customer(client)
    order_id = _create_order(client, owner_headers, category_id)["id"]

    ok = client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers=owner_headers,
        json={"status": "IN_PROGRESS"},
    )
    assert ok.status_code == 200
    assert ok.json()["status"] == "IN_PROGRESS"

    other_headers = _register_customer(client)
    forbidden = client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers=other_headers,
        json={"status": "CANCELED"},
    )
    assert forbidden.status_code == 403


def test_create_order_requires_authenticated_category(
    client: TestClient, admin_token: str
):
    headers = _register_customer(client)
    r = client.post(
        "/api/v1/orders/",
        headers=headers,
        json={
            "category_id": "00000000-0000-0000-0000-000000000000",
            "title": "Несуществующая категория",
            "description": "Описание заказа",
        },
    )
    assert r.status_code == 404