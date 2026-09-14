import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient

from app.main import create_app

SECRET = "webhook-secret"
TOOL_KEY = "tool-secret"
client = TestClient(
    create_app(
        database_url="sqlite+pysqlite:///:memory:",
        tool_api_key=TOOL_KEY,
        webhook_secret=SECRET,
    )
)


def signature(body: bytes, timestamp: int) -> str:
    digest = hmac.new(SECRET.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return f"t={timestamp},v0={digest}"


def auth() -> dict[str, str]:
    return {"Authorization": f"Bearer {TOOL_KEY}"}


def post_call_payload(conversation_id: str) -> dict[str, object]:
    return {
        "type": "post_call_transcription",
        "data": {
            "conversation_id": conversation_id,
            "agent_id": "agent-live-demo",
            "status": "done",
            "transcript": [
                {"role": "user", "message": "My phone is +52 33 0000 0000"},
                {"role": "agent", "message": "I can help with that."},
            ],
            "metadata": {
                "start_time_unix_secs": 1760000000,
                "call_duration_secs": 42,
                "cost": 60,
            },
            "analysis": {
                "transcript_summary": "Guest completed a safe demo interaction.",
                "evaluation_criteria_results": {"resolved": "success"},
            },
        },
    }


def deliver_post_call(conversation_id: str) -> None:
    body = json.dumps(post_call_payload(conversation_id), separators=(",", ":")).encode()
    timestamp = int(time.time())
    response = client.post(
        "/v1/webhooks/elevenlabs/post-call",
        content=body,
        headers={
            "ElevenLabs-Signature": signature(body, timestamp),
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 200


def test_post_call_audit_requires_authentication() -> None:
    response = client.get("/v1/ops/post-call-events/conv-ops-auth")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_ERROR"


def test_post_call_audit_exposes_verified_processed_event_without_raw_transcript() -> None:
    conversation_id = "conv-ops-visible"
    deliver_post_call(conversation_id)

    response = client.get(f"/v1/ops/post-call-events/{conversation_id}", headers=auth())

    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"] == conversation_id
    assert body["event_count"] == 1
    assert body["events"][0]["event_type"] == "post_call_transcription"
    assert body["events"][0]["processing_status"] == "processed"
    assert body["events"][0]["signature_verified"] is True
    assert body["conversation"] == {
        "agent_id": "agent-live-demo",
        "status": "done",
    }
    assert "Guest completed a safe demo interaction." not in response.text
    assert "+52 33 0000 0000" not in response.text


def test_post_call_audit_shows_single_event_after_duplicate_delivery() -> None:
    conversation_id = "conv-ops-idempotent"
    deliver_post_call(conversation_id)
    deliver_post_call(conversation_id)

    response = client.get(f"/v1/ops/post-call-events/{conversation_id}", headers=auth())

    assert response.status_code == 200
    assert response.json()["event_count"] == 1


def test_post_call_audit_returns_404_for_unknown_conversation() -> None:
    response = client.get("/v1/ops/post-call-events/conv-does-not-exist", headers=auth())

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_post_call_audit_marks_processing_failure() -> None:
    app = create_app(
        database_url="sqlite+pysqlite:///:memory:",
        tool_api_key=TOOL_KEY,
        webhook_secret=SECRET,
    )

    def fail_upsert(_: dict[str, object]) -> None:
        raise RuntimeError("simulated persistence failure")

    app.state.conversation_repository.upsert_from_post_call = fail_upsert
    failing_client = TestClient(app, raise_server_exceptions=False)
    conversation_id = "conv-ops-failed"
    body = json.dumps(post_call_payload(conversation_id), separators=(",", ":")).encode()
    timestamp = int(time.time())

    webhook_response = failing_client.post(
        "/v1/webhooks/elevenlabs/post-call",
        content=body,
        headers={
            "ElevenLabs-Signature": signature(body, timestamp),
            "Content-Type": "application/json",
        },
    )
    assert webhook_response.status_code == 500

    audit_response = failing_client.get(
        f"/v1/ops/post-call-events/{conversation_id}",
        headers=auth(),
    )
    assert audit_response.status_code == 200
    assert audit_response.json()["events"][0]["processing_status"] == "failed"


def test_failed_post_call_can_be_retried_and_processed() -> None:
    app = create_app(
        database_url="sqlite+pysqlite:///:memory:",
        tool_api_key=TOOL_KEY,
        webhook_secret=SECRET,
    )
    repository = app.state.conversation_repository
    original_upsert = repository.upsert_from_post_call
    attempts = 0

    def fail_once(payload: dict[str, object]) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("simulated transient persistence failure")
        original_upsert(payload)

    repository.upsert_from_post_call = fail_once
    retry_client = TestClient(app, raise_server_exceptions=False)
    conversation_id = "conv-ops-retry"
    body = json.dumps(post_call_payload(conversation_id), separators=(",", ":")).encode()

    first_timestamp = int(time.time())
    first = retry_client.post(
        "/v1/webhooks/elevenlabs/post-call",
        content=body,
        headers={
            "ElevenLabs-Signature": signature(body, first_timestamp),
            "Content-Type": "application/json",
        },
    )
    assert first.status_code == 500

    second_timestamp = int(time.time())
    second = retry_client.post(
        "/v1/webhooks/elevenlabs/post-call",
        content=body,
        headers={
            "ElevenLabs-Signature": signature(body, second_timestamp),
            "Content-Type": "application/json",
        },
    )
    assert second.status_code == 200
    assert second.json() == {"status": "processed"}

    audit = retry_client.get(f"/v1/ops/post-call-events/{conversation_id}", headers=auth())
    assert audit.status_code == 200
    assert audit.json()["event_count"] == 1
    assert audit.json()["events"][0]["processing_status"] == "processed"
