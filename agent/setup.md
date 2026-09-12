# ElevenAgents Setup

1. Create a new ElevenLabs Agent and choose a bilingual-capable voice appropriate for Spanish (Mexico) and English.
2. Paste `agent/prompt.md` as the system prompt.
3. Add `agent/knowledge-base.md` to the agent knowledge base.
4. Create the six webhook tools described in `agent/tool-contracts.json` and configure `Authorization: Bearer <TOOL_API_KEY>`.
5. Configure a post-call webhook to `POST /v1/webhooks/elevenlabs/post-call` using `ELEVENLABS_WEBHOOK_SECRET`.
6. Optionally configure an Agent Transfer system tool to a specialist/staff agent. The local repository records handoff business events but does not claim PSTN transfer.
7. Import the scenarios in `evals/scenarios.yaml` into ElevenLabs Agent Testing or reproduce them with equivalent tool-call criteria.

The repository is intentionally runnable without a real ElevenLabs API key; dashboard setup and live voice execution are external to the local backend tests.
