import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient

from app.main import create_app


SECRET = "webhook-secret"
client = TestClient(
    create_app(
        database_url="sqlite+pysqlite:///:memory:",
        tool_api_key="secret",
        webhook_secret=SECRET,
    )
)


def signature(body: bytes, timestamp: int) -> str:
    digest = hmac.new(SECRET.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return f"t={timestamp},v0={digest}"


def payload() -> dict[str, object]:
    return {
        "type": "post_call_transcription",
        "data": {
            "conversation_id": "conv-webhook-1",
            "agent_id": "agent-demo",
            "status": "done",
            "metadata": {"language": "es", "escalated": False},
            "analysis": {
                "transcript_summary": "Guest requested availability and received a booking link.",
                "evaluation_criteria_results": {"resolved": "success"},
            },
        },
    }


def test_rejects_invalid_signature() -> None:
    body = json.dumps(payload(), separators=(",", ":")).encode()
    response = client.post(
        "/v1/webhooks/elevenlabs/post-call",
        content=body,
        headers={"ElevenLabs-Signature": "t=1,v0=bad", "Content-Type": "application/json"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_ERROR"


def test_accepts_valid_signature_and_duplicate_is_idempotent() -> None:
    body = json.dumps(payload(), separators=(",", ":")).encode()
    timestamp = int(time.time())
    headers = {
        "ElevenLabs-Signature": signature(body, timestamp),
        "Content-Type": "application/json",
    }
    first = client.post("/v1/webhooks/elevenlabs/post-call", content=body, headers=headers)
    second = client.post("/v1/webhooks/elevenlabs/post-call", content=body, headers=headers)
    assert first.status_code == 200
    assert first.json() == {"status": "processed"}
    assert second.status_code == 200
    assert second.json() == {"status": "duplicate_ignored"}
