"""Offer & order 'my' endpoint tests (masters own offers / customer own orders)."""
import secrets

from fastapi.testclient import TestClient


def _register_and_token(client: TestClient, role: str) -> str:
    phone = "+9967" + "".join(str(secrets.randbelow(10)) for _ in range(8))
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": phone,
            "password": "secret123",
            "full_name": f"Test {secrets.token_hex(3)}",
            "role": role,
        },
    )
    assert reg.status_code == 201, reg.text
    return reg.json()["access_token"]


def _category(client: TestClient, admin_token: str) -> str:
    slug = f"cat-{secrets.token_hex(4)}"
    r = client.post(
        "/api/v1/categories/",
        json={"title": slug, "slug": slug},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_offers_my_requires_auth(client):
    assert client.get("/api/v1/offers/my").status_code == 401


def test_offers_my_forbidden_for_customer(client):
    customer_token = _register_and_token(client, "CUSTOMER")
    res = client.get(
        "/api/v1/offers/my", headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert res.status_code == 403


def test_master_offers_my_lists_own_offers(client, admin_token):
    cat_id = _category(client, admin_token)
    customer_token = _register_and_token(client, "CUSTOMER")
    master_token = _register_and_token(client, "MASTER")

    order = client.post(
        "/api/v1/orders/",
        json={"category_id": cat_id, "title": "Fix sink", "description": "Describe"},
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert order.status_code == 201, order.text

    offer = client.post(
        "/api/v1/offers/",
        json={
            "order_id": order.json()["id"],
            "proposed_price": "100.00",
            "comment": "ok",
        },
        headers={"Authorization": f"Bearer {master_token}"},
    )
    assert offer.status_code == 201, offer.text

    mine = client.get(
        "/api/v1/offers/my", headers={"Authorization": f"Bearer {master_token}"}
    )
    assert mine.status_code == 200
    assert any(o["id"] == offer.json()["id"] for o in mine.json())


def test_orders_my_lists_own_orders(client, admin_token):
    cat_id = _category(client, admin_token)
    customer_token = _register_and_token(client, "CUSTOMER")

    created = client.post(
        "/api/v1/orders/",
        json={"category_id": cat_id, "title": "Fix window", "description": "Desc"},
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert created.status_code == 201, created.text

    res = client.get(
        "/api/v1/orders/my", headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert res.status_code == 200
    assert any(o["id"] == created.json()["id"] for o in res.json())


def test_orders_my_requires_auth(client):
    assert client.get("/api/v1/orders/my").status_code == 401