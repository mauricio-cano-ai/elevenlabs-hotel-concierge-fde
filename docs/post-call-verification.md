# Verified post-call processing

The live ElevenLabs post-call flow is intentionally observable without exposing the full transcript.

```text
ElevenLabs post_call_transcription
        |
        | ElevenLabs-Signature (HMAC)
        v
POST /v1/webhooks/elevenlabs/post-call
        |
        +--> signature verification
        +--> SHA-256 delivery fingerprint / duplicate protection
        +--> conversation summary persistence
        +--> processing status: received -> processed | failed
        v
GET /v1/ops/post-call-events/{conversation_id}
```

The ops endpoint is protected with `Authorization: Bearer $TOOL_API_KEY`. A returned event has
`signature_verified: true` because invalid signatures are rejected before an event is persisted.
The endpoint deliberately omits the raw transcript; it returns only event metadata and the stored
conversation summary needed for demo verification.

## Live verification

After ending an ElevenLabs conversation, copy its conversation ID and run from PowerShell:

```powershell
$env:TOOL_API_KEY = "<your existing backend tool key>"
.\VERIFY_POST_CALL.ps1 -ConversationId "conv_..."
```

Expected shape:

```json
{
  "conversation_id": "conv_...",
  "event_count": 1,
  "events": [
    {
      "event_type": "post_call_transcription",
      "processing_status": "processed",
      "received_at": "...",
      "signature_verified": true
    }
  ],
  "conversation": {
    "agent_id": "...",
    "status": "done",
    "language": "es",
    "summary": "...",
    "escalated": false
  }
}
```

A repeated delivery of the same payload does not create a second event. The delivery fingerprint is
claimed once, so retries are idempotently returned as `duplicate_ignored` by the webhook handler.
