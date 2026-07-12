# DATA PING Thread Handoff Protocol v0.1

**Dato:** 2026-07-12  
**Status:** CANONICAL_OPERATIONAL  
**Område:** DATA PING thread ingestion / latest-source resolution / automation handoff  
**Primary folder:** `02_DATA_PING/`  
**Authority boundary:** source transport only; no independent analysis, market call, threshold change, rule promotion or portfolio action

## 1. Purpose

Make the user's DATA PING project thread the only user-facing input while giving scheduled framework tasks a durable, exact and machine-readable fallback.

The user is not required to open GitHub, create an Issue, copy a second payload or maintain a separate ledger.

## 2. Trigger

This protocol runs whenever the user posts a complete Custom GPT DATA PING analysis in an Investering project conversation.

A complete analysis is a structured DATA PING payload or full analysis containing the operative sensor/state fields. A casual question, correction request, acknowledgement or discussion message is not a new source payload.

## 3. Active-thread resolution

```text
1. Identify DATA PING version from thread title and/or payload metadata.
2. Maintain highest-version-used rule.
3. A higher version becomes active only after it contains an actual complete user-supplied DATA PING analysis.
4. Within the active highest version, latest complete analysis timestamp wins.
5. Older versions remain ARCHIVE_CONTEXT and may not update the live handoff.
6. If two same-version payloads have the same or ambiguous timestamp, set SOURCE_CONFLICT and do not replace the live pointer until resolved from message ordering/hash.
```

The currently known active version at protocol creation is `DATA PING V4`, subject to automatic supersession by a higher version actually used later.

## 4. Silent handoff sequence

For each eligible complete analysis:

1. Preserve the exact source message or exact structured payload without rewriting its claims.
2. Record:
   - DATA PING numeric version;
   - thread title;
   - source message timestamp;
   - ingestion timestamp;
   - schema version when present;
   - source data-quality labels;
   - stable SHA-256 or equivalent deterministic source hash;
   - raw/normalized payload path;
   - completeness status;
   - any explicit source conflicts or missing fields.
3. Write one dated append-only handoff artifact under:

```text
02_DATA_PING/operational_handoffs/history/YYYY-MM-DDTHHMMSSZ__data-ping-vN-thread-handoff.json
```

4. Read back the artifact and verify its hash and key metadata.
5. Only after successful verification, update:

```text
02_DATA_PING/operational_handoffs/latest_thread_source_state.json
```

6. Set `source_status=READY_THREAD_DERIVED` and `source_mode=THREAD_DERIVED` only after successful write/read-back.
7. Preserve the prior valid latest pointer if the new write fails.

## 5. Data boundary

The handoff may contain only information present in the user-supplied DATA PING analysis plus transport metadata.

Forbidden inside the handoff operation:

- web search;
- exchange/API supplementation;
- inferred missing values;
- independent market analysis;
- revised market conclusion;
- threshold or score mutation;
- portfolio action;
- retrospective reconstruction of an earlier missing ping.

Missing fields remain `DATA_MISSING`, `UNAVAILABLE` or the exact source label.

## 6. Duplicate and revision handling

- Same source hash: duplicate; do not create a second live source row.
- Same timestamp but different hash: `SOURCE_CONFLICT`.
- Later corrected payload explicitly supplied by the user: preserve both artifacts, mark revision lineage and let the corrected payload become latest only when clearly identified.
- A later casual message never changes the source pointer.
- An older DATA PING version never replaces the active higher-version pointer.

## 7. Integration

Primary consumers:

```text
Daily Sensor Pair Discovery Lab v0.1
Sunday Closeout
Master Monday
GitHub Archive Sync + Backup
other explicitly DATA-PING-aware prospective tests
```

Consumers must prefer direct accessible project-thread data. The handoff is a durable exact fallback, not a parallel source of market truth.

## 8. User notification

Normal successful handoffs are silent.

Notify only for:

- three consecutive eligible handoff write failures;
- unresolved same-version source conflict;
- version regression attempt;
- hash/read-back failure;
- schema corruption that makes the payload unusable.

## 9. Write governance

Repository writes use archive-governance, an isolated `agent/task-*` branch and a draft PR unless the active interactive task explicitly authorizes governed merge. Never write directly to `main` and never auto-merge scheduled runs.

## 10. Current status

```yaml
protocol_version: 0.1
highest_known_active_data_ping_version: 4
latest_exact_handoff: PENDING_NEXT_COMPLETE_DATA_PING
retrospective_handoffs_created: 0
user_github_action_required: NO
independent_market_data_fetch: FORBIDDEN
rule_promotion: NONE
portfolio_authority: ZERO
```
