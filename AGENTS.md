# AGENTS.md

## Project Goal

Build a digital human live streaming system for ecommerce live rooms.

Primary platforms:

- Taobao Live
- Douyin
- Xiaohongshu
- WeChat Channels
- Future: TikTok

The system must support digital human product explanation, comment handling, product RAG, AI answer generation, compliance review, human review, TTS, avatar playback, OBS/SRS media output, and audit logging.

## Non-Negotiable Architecture Rules

- Do not call platform APIs directly from business services.
- All platform integrations must go through `PlatformAdapter`.
- Do not call LLM providers directly from business logic.
- All LLM calls must go through `LLMGateway`.
- Do not call TTS providers directly from business logic.
- All TTS calls must go through `TTSService`.
- Do not couple LiveTalking directly with `LiveControlService`.
- All avatar commands must go through `AvatarGateway`.
- Do not bypass `ComplianceService` before digital human playback.
- Every AI-generated speech must pass compliance review before playback.
- Medium-risk and high-risk answers must require human review unless explicitly configured otherwise.
- Blocked answers must never be played.
- Every broadcasted sentence must be logged.
- Every live-state transition must be recorded.
- Every platform raw event must be stored or hash-logged for audit and debugging.
- Tests must not require real platform credentials.
- Use mock providers for platform, LLM, TTS, avatar, and media in automated tests.

## Security Rules

- Never commit secrets.
- Use environment variables or secret managers for credentials.
- Mask platform tokens, API keys, and user identifiers in logs.
- Do not store unnecessary personal data.
- Store platform raw payloads with configurable retention.
- Validate all uploaded files by type, size, and extension.
- Audio clone features must require a voice authorization record.
- Avatar assets must require ownership or usage authorization records.
- Do not implement unofficial scraping, packet capture, credential bypass, or platform anti-bot circumvention.
- If official platform APIs are unavailable, implement a `ManualInputAdapter` or `MockPlatformAdapter`, not a policy-violating workaround.

## Coding Stack

Backend:

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Redis + Redis Streams
- Qdrant
- MinIO-compatible object storage
- pytest
- ruff
- mypy where practical

Frontend:

- Vue 3
- TypeScript
- Element Plus
- Pinia
- Vue Router
- Axios
- WebSocket client
- ECharts for dashboards

Infrastructure:

- Docker Compose for local development
- Nginx gateway when needed
- SRS for RTMP/WebRTC preview and media routing
- OBS used on a streaming workstation, not necessarily containerized

## Directory Rules

- `apps/api-server`: FastAPI app entrypoint, routing, dependency injection, auth, OpenAPI.
- `apps/admin-web`: admin dashboard.
- `apps/control-web`: live control room dashboard.
- `services/platform-adapter`: platform adapter abstraction and implementations.
- `services/live-control`: live sessions, state machine, comment routing, speech queue, takeover.
- `services/product-rag`: products, SKU, FAQ, RAG indexing and retrieval.
- `services/llm-gateway`: LLM providers, prompt templates, model routing.
- `services/compliance`: rules, risk classification, human review workflow.
- `services/tts-service`: TTS provider abstraction, audio cache, voice licenses.
- `services/avatar-gateway`: Avatar provider abstraction, LiveTalking integration, mock avatar.
- `services/media-service`: SRS, stream health, recording, preview URLs.
- `packages/event-schema`: shared event schema.
- `packages/shared-types`: shared Pydantic/TypeScript types.
- `packages/prompt-templates`: versioned prompts.
- `infra`: local infrastructure configuration.
- `docs`: product, architecture, API, data, testing, deployment documentation.

## Development Rules

- Prefer small, testable modules.
- Prefer explicit state machines over implicit control flow.
- Use typed request/response schemas for every API.
- Use Alembic migrations for every database change.
- Add unit tests for every new service.
- Add integration tests for every important workflow.
- Include a mock provider before adding a real external provider.
- Do not introduce a new production dependency without explaining why.
- Update docs when changing public APIs, events, or state machine rules.

## Test Commands

Until the repository is fully bootstrapped, implement these commands in `Makefile`:

```bash
make install
make up
make down
make migrate
make seed
make test
make lint
make typecheck
make e2e
```

## Pull Request Expectations

Every PR must include:

- Summary of changes.
- Affected modules.
- Database migrations if any.
- Tests added/updated.
- Known limitations.
- Manual verification steps.
- Security and compliance considerations if the PR touches platform, AI, voice, avatar, or live playback.

## Done Definition

A task is not done until:

- Code compiles/runs.
- Tests pass.
- Public APIs are documented.
- Error cases are handled.
- Logs are structured and do not leak secrets.
- Mock tests do not depend on external credentials.
- Business rules in docs remain accurate.
