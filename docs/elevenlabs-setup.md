# ElevenLabs Setup Notes

Use `agent/setup.md` as the concise checklist. This document explains the integration choices.

- Webhook tools point to the public FastAPI base URL and use a bearer secret.
- Hotel static facts belong in the knowledge base; inventory/pricing do not.
- Configure post-call delivery to `/v1/webhooks/elevenlabs/post-call` and set the same signing secret as `ELEVENLABS_WEBHOOK_SECRET`.
- Agent transfer can route to a specialist agent or staff workflow. The public backend records the handoff request but intentionally does not pretend local demo mode completed a PSTN transfer.
- Use `evals/scenarios.yaml` as the source of truth for tool-call and conversational tests.


## Post-call verification

After the live webhook is configured with HMAC, use [`post-call-verification.md`](post-call-verification.md) and `VERIFY_POST_CALL.ps1` to verify signed delivery by ElevenLabs conversation ID without exposing the raw transcript.
