import secrets
import uuid

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
    return login.json()["access_token"]


def test_realtime_chat_flow(client: TestClient, admin_token: str):
    # Create category
    cat = client.post(
        "/api/v1/categories/",
        headers=_auth(admin_token),
        json={"title": "Сантехника", "slug": f"san-{secrets.token_hex(3)}"},
    )
    assert cat.status_code == 201
    category_id = cat.json()["id"]

    # Register customer and master
    customer_token = _register_and_login(client, "CUSTOMER")
    master_token = _register_and_login(client, "MASTER")

    # Customer creates order
    order = client.post(
        "/api/v1/orders/",
        headers=_auth(customer_token),
        json={
            "category_id": category_id,
            "title": "Fix sink",
            "description": "Leaking sink",
            "budget": "1000.00",
        },
    )
    assert order.status_code == 201
    order_id = order.json()["id"]

    # Master updates profile
    profile = client.put(
        "/api/v1/masters/profile",
        headers=_auth(master_token),
        json={"bio": "Plumber", "experience_years": 5, "category_ids": [category_id]},
    )
    assert profile.status_code == 200

    # Master posts offer
    offer = client.post(
        "/api/v1/offers/",
        headers=_auth(master_token),
        json={"order_id": order_id, "proposed_price": "900.00", "comment": "I can help"},
    )
    assert offer.status_code == 201
    offer_id = offer.json()["id"]

    # Customer accepts offer -> chat should be created
    accepted = client.post(f"/api/v1/offers/{offer_id}/accept", headers=_auth(customer_token))
    assert accepted.status_code == 200

    # Fetch chats for customer and find chat id
    chats = client.get("/api/v1/chats/", headers=_auth(customer_token))
    assert chats.status_code == 200
    assert len(chats.json()) >= 1
    chat_id = chats.json()[0]["id"]

    # Connect to websocket and send a message
    ws_url = f"/api/v1/chats/ws/{chat_id}?token={customer_token}"
    with client.websocket_connect(ws_url) as ws:
        # read join notification
        join = ws.receive_json()
        assert join.get("type") == "system"
        ws.send_json({"message_text": "Hello Master"})
        # receive broadcasted message
        msg = ws.receive_json()
        assert msg.get("type") == "message"
        assert msg.get("message_text") == "Hello Master"

    # Verify message persisted via REST
    msgs = client.get(f"/api/v1/chats/{chat_id}/messages", headers=_auth(customer_token))
    assert msgs.status_code == 200
    found = any(m["message_text"] == "Hello Master" for m in msgs.json())
    assert found
