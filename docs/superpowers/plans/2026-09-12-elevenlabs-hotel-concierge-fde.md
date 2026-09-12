# ElevenLabs Hotel Concierge FDE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build a public, production-style ElevenAgents hotel concierge integration demonstrating customer-facing architecture, Python engineering, secure API tools, post-call processing, tests, observability, and end-to-end ownership.

**Architecture:** ElevenAgents owns conversation/voice orchestration; a FastAPI service owns deterministic hotel business actions and webhook processing. A PMS adapter boundary provides deterministic local demo behavior, while SQLAlchemy persistence, idempotency, HMAC verification, structured errors, and audit events model production concerns.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2, httpx, pytest, pytest-cov, Ruff, mypy, Docker, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-12-elevenlabs-hotel-concierge-fde-design.md`

## Global Constraints

- No card/payment collection or processing.
- No claim of creating, modifying, or cancelling a real reservation.
- Local demo must run without live Cloudbeds/Mews credentials or Twilio/SIP.
- Core implementation is Python code, not no-code configuration.
- Tool endpoints are authenticated; secrets are environment-only.
- `capture-lead`, `request-handoff`, and post-call webhook processing are idempotent.
- ElevenLabs `conversation_id` is the primary correlation key where available.
- Tool failures expose typed safe errors, never stack traces or secrets.
- CI runs lint, typing, pytest/coverage, Docker build, and smoke test.

---

### Task 1: Domain contracts and deterministic PMS

**Files:** Create `pyproject.toml`, `app/__init__.py`, `app/config.py`, `app/models.py`, `app/integrations/pms/base.py`, `app/integrations/pms/demo.py`, `tests/unit/test_models.py`, `tests/unit/test_demo_pms.py`.

**Interfaces:** Produces Pydantic request/response models plus `PMSAdapter.check_availability()` and `DemoPMSAdapter` used by later services.

- [x] Write failing tests for date ordering, past dates, stay cap, and deterministic room options.
- [x] Run focused tests and confirm RED because app modules do not exist.
- [x] Implement minimal models/config/PMS adapter.
- [x] Run focused tests and confirm GREEN.

### Task 2: Business services

**Files:** Create `app/services/availability.py`, `quoting.py`, `booking_links.py`, `leads.py`, `handoff.py`, `tests/unit/test_services.py`.

**Interfaces:** Produces `AvailabilityService`, `QuoteService`, `BookingLinkService`, `LeadService`, `HandoffService` with deterministic outputs.

- [x] Write failing service tests for deterministic quote, safe booking link, and idempotent service contracts.
- [x] Verify RED.
- [x] Implement minimal services.
- [x] Verify GREEN.

### Task 3: Persistence and idempotency

**Files:** Create `app/persistence/database.py`, `app/persistence/repositories.py`, `tests/unit/test_repositories.py`.

**Interfaces:** Produces SQLite/PostgreSQL-compatible SQLAlchemy repositories for conversations, tool events, leads, handoffs, and webhook fingerprints.

- [x] Write failing repository tests for duplicate lead/handoff/webhook events.
- [x] Verify RED.
- [x] Implement schema/repositories and unique-key behavior.
- [x] Verify GREEN.

### Task 4: Security and API tools

**Files:** Create `app/security/tool_auth.py`, `app/api/tools.py`, `app/main.py`, `tests/integration/test_tools_api.py`.

**Interfaces:** Produces `/v1/tools/*`, `/healthz`, `/readyz`; bearer authentication via `TOOL_API_KEY`.

- [x] Write failing integration tests for auth, schemas, success, and typed failures.
- [x] Verify RED.
- [x] Implement dependencies/routes/error envelope and structured request logging.
- [x] Verify GREEN.

### Task 5: ElevenLabs post-call webhook

**Files:** Create `app/security/elevenlabs_webhook.py`, `app/services/outcomes.py`, `app/api/webhooks.py`, `tests/integration/test_post_call_webhook.py`.

**Interfaces:** Produces signature verification for `ElevenLabs-Signature`, duplicate fingerprint protection, conversation persistence, and safe outcome extraction.

- [x] Write failing tests for valid HMAC, invalid HMAC, post-call persistence, and duplicate delivery.
- [x] Verify RED.
- [x] Implement timestamp/HMAC verification over raw body and durable idempotent handling.
- [x] Verify GREEN.

### Task 6: ElevenAgents hiring artifact

**Files:** Create `agent/prompt.md`, `agent/tool-contracts.json`, `agent/knowledge-base.md`, `agent/setup.md`, `evals/scenarios.yaml`, `evals/README.md`.

**Interfaces:** Documents exact agent invariants/tool schemas and 12 evaluation scenarios mapped to ElevenLabs Agent Testing.

- [x] Validate JSON/YAML parseability with tests.
- [x] Add prompt/knowledge/tool contracts/eval catalog.
- [x] Run validation tests.

### Task 7: Documentation and customer-facing case study

**Files:** Create `README.md`, `docs/architecture.md`, `docs/customer-discovery.md`, `docs/failure-modes.md`, `docs/demo-script.md`, `docs/elevenlabs-setup.md`, `docs/fde-case-study.md`, `.env.example`, `LICENSE`.

**Interfaces:** Produces reviewer-first documentation: problem → architecture → setup → demo → tradeoffs → metrics.

- [x] Add executable setup commands and explicit real-vs-demo claims.
- [x] Add architecture/failure/customer discovery/FDE case study docs.
- [x] Verify every documented path/command exists.

### Task 8: Delivery, CI, smoke test, packaging

**Files:** Create `scripts/seed_demo.py`, `scripts/smoke_test.py`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `.gitignore`.

**Interfaces:** Produces local seed/smoke path and CI quality gates.

- [x] Add failing smoke/health checks where applicable.
- [x] Implement scripts/container/CI.
- [x] Run `ruff check .`, `ruff format --check .`, `mypy app`, `pytest --cov=app --cov-fail-under=85`, and smoke test.
- [x] Build Docker image.
- [x] Create ZIP artifact after all gates pass.
