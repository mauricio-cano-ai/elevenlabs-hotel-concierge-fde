from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Iterator

from sqlalchemy import Boolean, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class ConversationRow(Base):
    __tablename__ = "conversations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    agent_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="completed")
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    success_outcome: Mapped[str | None] = mapped_column(String(80), nullable=True)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)


class LeadRow(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[str] = mapped_column(String(64), unique=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    conversation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payload_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class HandoffRow(Base):
    __tablename__ = "handoff_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    handoff_id: Mapped[str] = mapped_column(String(64), unique=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    conversation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reason: Mapped[str] = mapped_column(Text)
    urgency: Mapped[str] = mapped_column(String(20))
    context_summary: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(40), default="requested")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class WebhookEventRow(Base):
    __tablename__ = "webhook_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80))
    conversation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(40), default="processed")
    received_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class ToolEventRow(Base):
    __tablename__ = "tool_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True)
    conversation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    tool_name: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40))
    latency_ms: Mapped[int] = mapped_column(Integer)
    safe_request_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    safe_response_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class Database:
    def __init__(self, url: str) -> None:
        kwargs = {}
        if url.endswith(":memory:"):
            kwargs = {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
        self.engine = create_engine(url, future=True, **kwargs)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
