# Architecture

## Boundary choice

ElevenAgents is the conversational runtime. The backend deliberately does not rebuild speech recognition, TTS, turn detection, or agent dialogue orchestration. That keeps this repository focused on the work an FDE owns around a strategic customer: system integration, deterministic business logic, safety, observability, and delivery quality.

## Data flow

1. Guest speaks or chats with the ElevenAgent.
2. Static hotel questions resolve from knowledge; inventory/pricing triggers authenticated webhook tools.
3. FastAPI validates inputs and calls the PMS adapter.
4. Side effects use idempotency keys and persist durable business events.
5. After the conversation, ElevenLabs sends a signed post-call payload; the API verifies the raw body before trusting the event and deduplicates it by body fingerprint.
6. `conversation_id` is the join key between the platform conversation and application-side events.

## PMS boundary

`DemoPMSAdapter` is deterministic and runnable by reviewers. `CloudbedsAdapter` and `MewsAdapter` exist only as explicit contracts and fail closed until real customer credentials, API semantics, retry policy, and rate limits are configured.
