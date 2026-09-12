# Failure Modes and Response Policy

| Failure | Detection | Agent-safe behavior | Engineering behavior |
|---|---|---|---|
| Invalid dates | Pydantic validation | ask guest to clarify | return validation error, no PMS call |
| PMS timeout | adapter timeout | say availability cannot be verified; offer staff | bounded retry only for safe reads; typed `PMS_TIMEOUT` |
| PMS unavailable | adapter error | offer handoff | typed `PMS_UNAVAILABLE`; log correlation IDs |
| Duplicate lead | unique idempotency key | continue normally | return existing lead ID, no duplicate row |
| Duplicate handoff | unique idempotency key | continue normally | return existing handoff ID |
| Duplicate post-call | body fingerprint | no guest impact | return `duplicate_ignored` |
| Invalid webhook signature | HMAC/timestamp validation | n/a | 401 before trusting/parsing event semantics |
| Payment request | prompt invariant | refuse card data and offer booking link/staff | never persist payment fields |
| Tool unavailable | tool error | disclose limitation; never invent | safe error envelope, no stack trace |

The public demo intentionally fails closed for Cloudbeds/Mews because fake integration success would be a worse engineering signal than an explicit adapter contract.
