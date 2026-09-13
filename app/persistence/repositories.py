from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import cast
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
                if existing.processing_status == "failed":
                    existing.processing_status = "received"
                    return True
                return False
            session.add(
                WebhookEventRow(
                    fingerprint=fingerprint,
                    event_type=event_type,
                    conversation_id=conversation_id,
                    processing_status="received",
                )
            )
            return True

    def mark_status(self, fingerprint: str, status: str) -> None:
        with self.db.session() as session:
            row = session.scalar(
                select(WebhookEventRow).where(WebhookEventRow.fingerprint == fingerprint)
            )
            if row is not None:
                row.processing_status = status

    def list_for_conversation(self, conversation_id: str) -> list[WebhookEventRow]:
        with self.db.session() as session:
            return list(
                session.scalars(
                    select(WebhookEventRow)
                    .where(WebhookEventRow.conversation_id == conversation_id)
                    .order_by(WebhookEventRow.received_at.asc())
                )
            )


class ConversationRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_by_conversation_id(self, conversation_id: str) -> ConversationRow | None:
        with self.db.session() as session:
            return session.scalar(
                select(ConversationRow).where(ConversationRow.conversation_id == conversation_id)
            )

    def upsert_from_post_call(self, payload: dict[str, object]) -> None:
        raw_data = payload.get("data")
        data = cast(dict[str, object], raw_data) if isinstance(raw_data, dict) else payload

        conversation_id = str(data.get("conversation_id") or payload.get("conversation_id") or "")
        if not conversation_id:
            return
        raw_analysis = data.get("analysis")
        analysis = cast(dict[str, object], raw_analysis) if isinstance(raw_analysis, dict) else {}

        raw_metadata = data.get("metadata")
        metadata = cast(dict[str, object], raw_metadata) if isinstance(raw_metadata, dict) else {}

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
