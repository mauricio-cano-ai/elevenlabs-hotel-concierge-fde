from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:", tool_api_key="secret"))


def auth() -> dict[str, str]:
    return {"Authorization": "Bearer secret"}


def test_tool_requires_authentication() -> None:
    response = client.get("/v1/tools/hotel-information")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_ERROR"


def test_availability_tool_returns_options() -> None:
    check_in = date.today() + timedelta(days=5)
    response = client.post(
        "/v1/tools/check-availability",
        headers=auth(),
        json={
            "check_in": check_in.isoformat(),
            "check_out": (check_in + timedelta(days=2)).isoformat(),
            "adults": 2,
            "children": 0,
            "conversation_id": "conv-api-1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["available"] is True
    assert body["options"][0]["room_type"] == "Deluxe King"


def test_capture_lead_is_idempotent() -> None:
    payload = {
        "idempotency_key": "lead-api-123",
        "conversation_id": "conv-api-2",
        "guest_name": "Mariana López",
        "phone": "+523311111111",
        "language": "es",
    }
    first = client.post("/v1/tools/capture-lead", headers=auth(), json=payload)
    second = client.post("/v1/tools/capture-lead", headers=auth(), json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["lead_id"] == second.json()["lead_id"]
    assert first.json()["created"] is True
    assert second.json()["created"] is False


def test_health_and_readiness() -> None:
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").json()["status"] == "ready"
