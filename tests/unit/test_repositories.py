from datetime import date, timedelta

from app.models import HandoffRequest, LeadCaptureRequest
from app.persistence.database import Database
from app.persistence.repositories import HandoffRepository, LeadRepository, WebhookEventRepository


def test_lead_upsert_is_idempotent() -> None:
    db = Database("sqlite+pysqlite:///:memory:")
    repo = LeadRepository(db)
    check_in = date.today() + timedelta(days=10)
    request = LeadCaptureRequest(
        idempotency_key="lead-key-123",
        conversation_id="conv-1",
        guest_name="Ana Ruiz",
        phone="+523300000000",
        check_in=check_in,
        check_out=check_in + timedelta(days=2),
        adults=2,
    )
    first = repo.capture(request)
    second = repo.capture(request)
    assert first.lead_id == second.lead_id
    assert first.created is True
    assert second.created is False


def test_handoff_is_idempotent() -> None:
    db = Database("sqlite+pysqlite:///:memory:")
    repo = HandoffRepository(db)
    request = HandoffRequest(
        idempotency_key="handoff-123",
        conversation_id="conv-1",
        reason="Guest requested staff",
        context_summary="Wants to speak with reception.",
    )
    first = repo.request(request)
    second = repo.request(request)
    assert first.handoff_id == second.handoff_id
    assert first.created is True
    assert second.created is False


def test_webhook_fingerprint_is_processed_once() -> None:
    db = Database("sqlite+pysqlite:///:memory:")
    repo = WebhookEventRepository(db)
    assert repo.claim("fingerprint", "post_call_transcription", "conv-1") is True
    assert repo.claim("fingerprint", "post_call_transcription", "conv-1") is False
