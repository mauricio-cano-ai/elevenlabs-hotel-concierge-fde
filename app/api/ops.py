from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.models import ConversationAudit, PostCallAuditResponse, PostCallEventAudit
from app.security.tool_auth import require_tool_auth

router = APIRouter(prefix="/v1/ops", dependencies=[Depends(require_tool_auth)])


@router.get("/post-call-events/{conversation_id}", response_model=PostCallAuditResponse)
def post_call_events(conversation_id: str, request: Request) -> PostCallAuditResponse:
    events = request.app.state.webhook_repository.list_for_conversation(conversation_id)
    if not events:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "No verified post-call event found for this conversation",
                "retryable": False,
            },
        )

    conversation_row = request.app.state.conversation_repository.get_by_conversation_id(
        conversation_id
    )
    conversation = None
    if conversation_row is not None:
        conversation = ConversationAudit(
            agent_id=conversation_row.agent_id,
            status=conversation_row.status,
        )

    return PostCallAuditResponse(
        conversation_id=conversation_id,
        event_count=len(events),
        events=[
            PostCallEventAudit(
                event_type=event.event_type,
                processing_status=event.processing_status,
                received_at=event.received_at,
            )
            for event in events
        ],
        conversation=conversation,
    )
