# Decision Log

Architectural decisions and rationales for RAG Health POC.

---

## Data Source

**Decision:** Use DailyMed SPL XML as primary data source.

**Rationale:**
- Structured sections with stable anchor IDs enable precise citations
- Official FDA source with public API
- XML parsing allows clean extraction vs. PDF text layer issues

---

## Embeddings

**Decision:** OpenAI `text-embedding-3-large` (3072-dim).

**Rationale:**
- Best quality-to-cost ratio for POC
- Easy swap to open models (via `Settings.openai_embedding_model`)
- Consistent with production OpenAI usage

---

## Vector Store

**Decision:** Redis Stack with HNSW index.

**Rationale:**
- Single binary for dev (Redis + search + JSON)
- Fast KNN with metadata filtering (drug, section, version)
- Simpler ops than dedicated vector DB for POC scale
- Built-in RedisInsight for debugging

---

## Agent Framework

**Decision:** LangGraph with small state machine (5 nodes).

**Rationale:**
- Explicit verification step (citations, confidence) vs. single LLM call
- Observable state transitions for debugging
- Easy to add retries/fallbacks per node
- Low abstraction overhead vs. heavy agent frameworks

---

## Prompt Strategy

**Decision:** Minimal system prompt with strict citation enforcement.

**Rationale:**
- Testable: regex check for `[Section: X] (url#section=Y)`
- Grounded: explicit "Not in context" fallback
- Concise: prioritize numbers (dose, interval) over prose

---

## Chunking

**Decision:** 1536 tokens, 150 overlap, tiktoken-based.

**Rationale:**
- Fits embedding model context
- Overlap preserves context across splits
- Token-based ensures uniform semantic density vs. character splits

---

## Observability

**Decision:** W&B for traces and evals; no custom logging infra.

**Rationale:**
- Fast POC iteration with built-in dashboards
- Eval regression gates (grounding rate, latency p95)
- Team already uses W&B (assumed)

---

## Monorepo Structure

**Decision:** uv workspace for Python; reserved pnpm workspace for future JS.

**Rationale:**
- Shared types between API and evals
- Single lockfile for reproducibility
- Easy to add `apps/crawler` or `apps/web` later
- Justfile tasks work across all apps

---

## Compliance

**Decision:** Public data only; mandatory disclaimers; no PHI.

**Rationale:**
- DailyMed data is public domain
- Disclaimers protect against misuse
- Citation links allow user verification

---

## Section Mapping

**Decision:** Map LOINC codes to normalized names (e.g., `34067-9` → `INDICATIONS_AND_USAGE`).

**Rationale:**
- Stable across SPL versions
- Human-readable in filters
- Aligns with FDA section naming

---

## Deduplication

**Decision:** Dedupe retrieved contexts by `section_id`.

**Rationale:**
- Avoid redundant chunks from same section
- Users see diverse sections (dosage, contraindications, etc.)
- Still keep top-K for relevance ranking

---

## Confidence Threshold

**Decision:** 0.7 default; fallback message if below + no citations.

**Rationale:**
- Balances recall (answer most queries) vs. precision (avoid low-quality)
- Citation check overrides score (explicit grounding signal)
- Tunable via `Settings.confidence_threshold`

---

## CI Strategy

**Decision:** GitHub Actions with lint/typecheck mandatory; evals non-blocking initially.

**Rationale:**
- Fast feedback on PRs (ruff + mypy run in <10s)
- Evals take ~30s; gate after baseline stabilizes
- Allow eval failures during iteration phase

---

## API Design

**Decision:** Single `/ask` endpoint; separate `/ingest/{drug}` for data loading.

**Rationale:**
- Simple REST for frontend integration
- Ingestion separated from query path (no runtime blocking)
- Health/stats endpoints for ops monitoring

---

## Docker Setup

**Decision:** Docker Compose for local dev; Redis-only by default.

**Rationale:**
- API runs natively for fast reload (`just dev-api`)
- Redis in container for consistent state
- Full stack (`just up`) available for E2E testing

---

## Error Handling

**Decision:** Graceful fallbacks at each agent node; HTTP 500 only on infra failures.

**Rationale:**
- "Not in context" message vs. error on empty retrieval
- Redis/LLM failures return 500 (ops issue)
- User queries always get response (may be "insufficient context")

---

## Future Extensions

**Decisions deferred:**

- Multi-label synthesis (compare drugs): requires query decomposition node
- Auto-crawlers: needs robots.txt parser + scheduler
- Frontend: Next.js with citation highlights (citation IDs already in response)
- Advanced evals: hallucination detection (LLM-as-judge or NLI model)

**Rationale:** Prioritize core RAG quality + observability for POC; expand after validation.

---

*Last updated: 2025-10-18*
