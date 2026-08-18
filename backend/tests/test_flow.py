"""End-to-end marketplace flow: order -> offer -> accept -> complete -> review."""
import secrets

from fastapi.testclient import TestClient


def _phone() -> str:
    return "+9967" + "".join(str(secrets.randbelow(10)) for _ in range(8))


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register_and_login(client: TestClient, role: str) -> dict:
    phone = _phone()
    client.post(
        "/api/v1/auth/register",
        json={
            "phone_number": phone,
            "password": "secret123",
            "full_name": f"User {role}",
            "role": role,
        },
    )
    login = client.post(
        "/api/v1/auth/login", data={"username": phone, "password": "secret123"}
    )
    assert login.status_code == 200, login.text
    return _auth(login.json()["access_token"])


def test_full_marketplace_flow(client: TestClient, admin_token: str):
    # 1. Admin creates a service category
    cat = client.post(
        "/api/v1/categories/",
        headers=_auth(admin_token),
        json={"title": "Ремонт", "slug": f"repair-{secrets.token_hex(3)}"},
    )
    assert cat.status_code == 201, cat.text
    category_id = cat.json()["id"]

    # 2. Customer creates an order
    customer_headers = _register_and_login(client, "CUSTOMER")
    order = client.post(
        "/api/v1/orders/",
        headers=customer_headers,
        json={
            "category_id": category_id,
            "title": "Починить кран",
            "description": "Течёт кран на кухне",
            "budget": "2000.00",
        },
    )
    assert order.status_code == 201, order.text
    order_id = order.json()["id"]

    # 3. Master updates profile with categories
    master_headers = _register_and_login(client, "MASTER")
    profile = client.put(
        "/api/v1/masters/profile",
        headers=master_headers,
        json={
            "bio": "Сантехник с 10-летним опытом",
            "experience_years": 10,
            "category_ids": [category_id],
        },
    )
    assert profile.status_code == 200, profile.text
    master_id = profile.json()["id"]
    assert profile.json()["categories"][0]["id"] == category_id

    # 4. Master submits an offer
    offer = client.post(
        "/api/v1/offers/",
        headers=master_headers,
        json={"order_id": order_id, "proposed_price": "1800.00", "comment": "Могу прийти завтра"},
    )
    assert offer.status_code == 201, offer.text
    offer_id = offer.json()["id"]

    # 5. Customer lists offers for the order
    offers = client.get(f"/api/v1/offers/order/{order_id}", headers=customer_headers)
    assert offers.status_code == 200
    assert offers.json()[0]["master_full_name"].startswith("User MASTER")

    # 6. Customer accepts the offer -> order becomes IN_PROGRESS
    accepted = client.post(f"/api/v1/offers/{offer_id}/accept", headers=customer_headers)
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["status"] == "ACCEPTED"

    # 7. Customer marks the order COMPLETED
    done = client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers=customer_headers,
        json={"status": "COMPLETED"},
    )
    assert done.status_code == 200
    assert done.json()["status"] == "COMPLETED"

    # 8. Customer reviews the completed order; master rating updates
    review = client.post(
        "/api/v1/reviews/",
        headers=customer_headers,
        json={"order_id": order_id, "rating": 5, "comment": "Отлично!"},
    )
    assert review.status_code == 201, review.text
    assert review.json()["rating"] == 5

    master_profile = client.get(f"/api/v1/masters/{master_id}")
    assert master_profile.status_code == 200
    assert master_profile.json()["rating"] == 5.0
    assert master_profile.json()["reviews_count"] == 1

    # 9. Duplicate review for the same order is rejected
    dup = client.post(
        "/api/v1/reviews/",
        headers=customer_headers,
        json={"order_id": order_id, "rating": 1},
    )
    assert dup.status_code == 409