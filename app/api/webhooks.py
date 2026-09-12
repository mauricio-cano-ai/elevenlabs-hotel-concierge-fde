from __future__ import annotations

import hashlib
import json

from fastapi import APIRouter, HTTPException, Request

from app.security.elevenlabs_webhook import WebhookSignatureError, verify_elevenlabs_signature

router = APIRouter(prefix="/v1/webhooks/elevenlabs")


@router.post("/post-call")
async def post_call(request: Request) -> dict[str, str]:
    raw_body = await request.body()
    try:
        verify_elevenlabs_signature(
            raw_body,
            request.headers.get("ElevenLabs-Signature"),
            request.app.state.settings.elevenlabs_webhook_secret,
            request.app.state.settings.webhook_tolerance_seconds,
        )
    except WebhookSignatureError as exc:
        raise HTTPException(
            status_code=401,
            detail={"code": "AUTH_ERROR", "message": str(exc), "retryable": False},
        ) from exc
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Invalid JSON",
                "retryable": False,
            },
        ) from exc
    if payload.get("type") != "post_call_transcription":
        return {"status": "ignored"}
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    conversation_id = str(data.get("conversation_id") or "") or None
    fingerprint = hashlib.sha256(raw_body).hexdigest()
    claimed = request.app.state.webhook_repository.claim(
        fingerprint, "post_call_transcription", conversation_id
    )
    if not claimed:
        return {"status": "duplicate_ignored"}
    request.app.state.conversation_repository.upsert_from_post_call(payload)
    return {"status": "processed"}
