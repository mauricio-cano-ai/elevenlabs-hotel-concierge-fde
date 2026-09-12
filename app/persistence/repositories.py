from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select

from app.models import HandoffRequest, HandoffResponse, LeadCaptureRequest, LeadCaptureResponse
from app.persistence.database import ConversationRow, Database, HandoffRow, LeadRow, WebhookEventRow


class LeadRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def capture(self, request: LeadCaptureRequest) -> LeadCaptureResponse:
        with self.db.session() as session:
            existing = session.scalar(
                select(LeadRow).where(LeadRow.idempotency_key == request.idempotency_key)
            )
            if existing:
                return LeadCaptureResponse(lead_id=existing.lead_id, created=False)
            lead_id = str(uuid4())
            session.add(
                LeadRow(
                    lead_id=lead_id,
                    idempotency_key=request.idempotency_key,
                    conversation_id=request.conversation_id,
                    payload_json=request.model_dump_json(),
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
            )
            return LeadCaptureResponse(lead_id=lead_id, created=True)


class HandoffRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def request(self, request: HandoffRequest) -> HandoffResponse:
        with self.db.session() as session:
            existing = session.scalar(
                select(HandoffRow).where(HandoffRow.idempotency_key == request.idempotency_key)
            )
            if existing:
                return HandoffResponse(handoff_id=existing.handoff_id, created=False)
            handoff_id = str(uuid4())
            session.add(
                HandoffRow(
                    handoff_id=handoff_id,
                    idempotency_key=request.idempotency_key,
                    conversation_id=request.conversation_id,
                    reason=request.reason,
                    urgency=request.urgency,
                    context_summary=request.context_summary,
                )
            )
            return HandoffResponse(handoff_id=handoff_id, created=True)


class WebhookEventRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def claim(self, fingerprint: str, event_type: str, conversation_id: str | None) -> bool:
        with self.db.session() as session:
            existing = session.scalar(
                select(WebhookEventRow).where(WebhookEventRow.fingerprint == fingerprint)
            )
            if existing:
                return False
            session.add(
                WebhookEventRow(
                    fingerprint=fingerprint,
                    event_type=event_type,
                    conversation_id=conversation_id,
                )
            )
            return True


class ConversationRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def upsert_from_post_call(self, payload: dict[str, object]) -> None:
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        assert isinstance(data, dict)
        conversation_id = str(data.get("conversation_id") or payload.get("conversation_id") or "")
        if not conversation_id:
            return
        analysis = data.get("analysis") if isinstance(data.get("analysis"), dict) else {}
        metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        with self.db.session() as session:
            row = session.scalar(
                select(ConversationRow).where(ConversationRow.conversation_id == conversation_id)
            )
            if row is None:
                row = ConversationRow(conversation_id=conversation_id)
                session.add(row)
            row.agent_id = str(data.get("agent_id")) if data.get("agent_id") else None
            row.status = str(data.get("status") or "completed")
            row.language = str(metadata.get("language")) if metadata.get("language") else None
            transcript_summary = analysis.get("transcript_summary")
            row.summary = str(transcript_summary) if transcript_summary else None
            evaluation = analysis.get("evaluation_criteria_results")
            row.success_outcome = json.dumps(evaluation, default=str) if evaluation else None
            row.escalated = bool(metadata.get("escalated", False))
