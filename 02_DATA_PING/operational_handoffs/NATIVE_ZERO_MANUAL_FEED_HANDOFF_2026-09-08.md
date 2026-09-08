# Native Zero-Manual-Feed Operating Model — Handoff

Date: 2026-09-08
Authority repo: Donh91/Investering-Framework-Archive-v1
Issue: #822
Branch: feat/native-handlekompas-zero-manual-feed-20260908

## User directive

Manual market-data feeding is retired as a normal operating dependency. If a market variable can be fetched reproducibly by an existing GitHub owner, API, deterministic source adapter, or admitted discovery lane, the framework must collect, validate, timestamp, archive and use it automatically.

The user may ask only for short readbacks such as `Kompas`, `Handlekompas`, `Status`, `CN`, `Data Ping`, or `OTA`. These prompts must read the latest verified GitHub-native state instead of asking the user to paste market data.

Manual Custom-GPT Data Ping remains diagnostic/fallback only and must never become the primary predecessor store.

## Required native chain

sources -> unattended GitHub owners -> frozen owner snapshot -> AUTO_MARKET_STATE_PACKET_v1 -> Handlekompas -> Entry Signal / Cycle Navigator / OTA / learning

GitHub, not chat history, owns predecessor continuity, deltas, provenance, freshness, degradation and receipts.

## Failure policy

- Repeated operational failures should be repaired automatically where a deterministic, non-destructive recovery path exists.
- Missing, stale, ambiguous or non-reproducible data remains UNKNOWN/DEGRADED/UNAVAILABLE; never silently substituted.
- Pointer/readback mismatch must fail closed and preserve last verified evidence.
- Missing ledger receipts/hashes must not be reconstructed post-hoc.
- Provider/auth/quota/token/budget exhaustion must be surfaced explicitly as operational health, not interpreted as market evidence.
- CFGI failures must distinguish at minimum authentication, quota/rate-limit/token-budget exhaustion, schema/source failure and unknown failure when evidence permits.

## Budget policy

Automation should optimize information value per cost. Cadence may adapt within existing governance, but portfolio authority, canonical thresholds and historical evidence may not be mutated automatically. If a configured monthly budget, provider quota, API token allowance or model usage budget is exhausted or near exhaustion, the Handlekompas and Master Monday outputs must say so plainly.

## Readback semantics

### `Kompas` / `Handlekompas`
Return concise current action context from latest verified native owner state:
- NOW
- PREPARE
- TOPUP_GATE
- RISK_DOWN
- DATA_HEALTH
- BUDGET_HEALTH
- WHY

No autonomous portfolio execution.

### `Status`
Return short market-state delta and machinery health since prior accepted native state.

### `Data Ping`
Read latest native state and audit/interpret it. Do not launch a redundant manual collector merely because the phrase Data Ping was used.

### `CN`
Read current Cycle Navigator public/canonical machine package plus current contextual native state. Live context must never silently rewrite the frozen weekly signal.

### `OTA`
Read latest Native OTA state; run additional research only when the adaptive gate or explicit user request warrants it.

## Graduation gate

The zero-manual-feed model is operationally promoted only after:
1. Handlekompas is generated from pinned owner state with deterministic validation.
2. Repeated pointer/freshness issues are bounded by native readback/recovery.
3. Provider/budget health is machine-readable and surfaced in readbacks.
4. CI passes on the implementation branch.
5. PR merges to main and main readback verifies the promoted contracts.

Until graduation, existing owners remain authoritative for their lanes and the new aggregation/output layer remains non-binding.
