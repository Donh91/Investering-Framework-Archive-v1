# Weekly Intelligence Audit — bounded implementation review (2026-10-19)

Status: PROPOSED / NOT PRODUCTION-ACTIVE. Evidence-based code audit; no market-state, forecast, scientific-admission, budget or portfolio authority.

## Scope and governing authority
- Existing `AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2`, Daily Capture v2.2, Master Monday producer and CN owner remain authoritative.
- GitHub Actions alone may publish weekly durable output, after validating immutable input and consumer readback. This proposal is **not** a new scheduler, pointer, queue, writer or source of truth.
- Never copy restricted provider payloads, secrets or private normalized data into public logs.
- No retrospective repair or backfilling; start only on the next naturally eligible weekly run after separately reviewed implementation.

## Verified W42 evidence (read from current main, 2026-10-19)
- `research/api_agent/outputs/weekly/2026/W42/MASTER_MONDAY_DELIVERY_POINTER.json`: producer READY, consumer VERIFIED/PASS, preflight FULL_MASTER_MONDAY_INPUT; `scorecard_status=UNAVAILABLE_API_CONTRACT`, `operational_translation_status=UNAVAILABLE_API_CONTRACT`, learning impact `NOT_EVALUABLE_NOVEL_INPUT_NOT_CONSUMED`.
- `research/api_agent/outputs/weekly/2026/W42/MASTER_MONDAY_MACHINE_PACKAGE.json`: validated `WEEKLY_CALIBRATION_SHADOW` response does not contain scorecard/operational_translation; fallback scorecard counts 140 matured registry outcomes but does not assert their scientific admission or score.
- `scripts/master_monday/publish_master_monday_outputs.py`: `api.get('operational_translation')` defaults to `UNAVAILABLE_API_CONTRACT`; `api.get('scorecard')` defaults via `fallback_scorecard`. Consumer PASS verifies declared freeze/preflight, not analytical completeness.
- `05_CYCLE_NAVIGATOR/weekly/2026/W43/CYCLE_NAVIGATOR_FORECAST_FREEZE.json`: daily expected-close path explicitly UNAVAILABLE with reasons; frozen scenario ranges and bull/bear evidence balance exist. Do not manufacture daily closes or phase ETA.
- `scripts/cycle_navigator/build_weekly_cycle_navigator.py`: `current_phase` schema explicitly permits `UNAVAILABLE`; this alone does not prove a broken upstream phase edge.
- `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`: AMBER fleet, 193 GREEN / 5 AMBER / 0 RED at audit time. This is fleet health, not weekly report completeness.

## P0 — API output completeness (two independent contract fields)
1. Trace the actual `WEEKLY_CALIBRATION_SHADOW` request schema, validated response parser and publisher; do not merely remove the publisher fallback.
2. Define schema-bound, optional or required fields for `scorecard` and `operational_translation` under the current domain owner's authority. Never infer a scored outcome from a matured count; never auto-promote a shadow result.
3. Keep distinct statuses: `API_FAILED`, `FIELD_NOT_IN_CONTRACT`, `FIELD_MISSING`, `SOURCE_UNAVAILABLE`, `INSUFFICIENT_EVIDENCE`, `NOT_APPLICABLE`, and `VALID`. A consumer receipt PASS is orthogonal to analytical completeness.
4. Negative tests: API failure; missing field on successful API call; malformed field; matured-but-unscored registry; unavailable registry; conflicting source identity; incomplete receipt; stale or wrong-week freeze. Positive control: valid hash-bound scorecard and non-trading operational translation.
5. Verify test sensitivity by mutating/removing relevant guards; do not claim tests passed without executing them.

## P1 — canonical phase provenance and ETA
- Resolve exact canonical phase owner, accepted source/gates and consumer identity. Diagnose `UNAVAILABLE` as one of: no canonical phase; stale source; missing link; conflicting evidence; genuinely insufficient evidence. Never replace absence with inferred phase or countdown.
- Log confirmed vs missing canonical gates and provenance; do not double-count correlated signals.
- Require explicit status and reason on each phase field and ETA. An unsupported ETA must remain NOT_ESTIMABLE.

## P1 — append-only weekly machine audit (existing weekly writer only)
Implement one compact `Wxx_WEEKLY_INTELLIGENCE_AUDIT.md` alongside the existing weekly Master Monday output, only if the existing weekly owner accepts the addition. Content should be machine-oriented, minimal and deterministically assembled from immutable references; do not introduce a new `LATEST` authority.

Suggested sections:
```yaml
contract: WEEKLY_INTELLIGENCE_AUDIT_PROPOSAL_v1
iso_week: YYYY-Www
produced_at_utc: <UTC>
writer: EXISTING_MASTER_MONDAY_ACTION
source_refs:
  preflight: {path: ..., sha256: ..., status: ...}
  weekly_close: {path: ..., sha256: ..., status: ...}
  hourly_calibration: {path: ..., sha256: ..., status: ...}
  freeze: {path: ..., sha256: ..., status: ...}
  api_receipt: {path: ..., sha256: ..., status: ...}
  machine_package: {path: ..., sha256: ..., status: ...}
  delivery_pointer: {path: ..., sha256: ..., status: ...}
  cn_forecast_freeze: {path: ..., sha256: ..., status: ...}
phase: {canonical_owner: ..., label: ..., status: ..., reason: ..., confirmed_gates: [], missing_gates: [], eta_status: ...}
source_health: [{id: ..., freshness: ..., evidence_class: ..., status: ..., reason: ...}]
accountability: {forecast_identity: ..., horizon: ..., maturity: ..., score: ..., admission: ..., contract: ...}
learning: {input_identity: ..., consumed: ..., impact_status: ..., decision_changed: ...}
completeness: {preflight: ..., api: ..., consumer: ..., analysis: ..., status: ...}
followups: [{finding_id: ..., existing_owner: ..., evidence_ref: ..., next_gate: ...}]
```
All `...` values are placeholders, **not** observed evidence. If a field is absent, preserve typed missingness; do not synthesize values.

## P2 — scientific and operational firewalls
- Only exact eligible canonical frozen outcomes may be scored. Keep MATURED, SCORED, CENSORED, PENDING, SPEC_REQUIRED, and scientific ADMITTED separate.
- Report `FORECAST_SKILL: UNPROVEN` until the accepted preregistered inferential test is met. Never rewrite historical freezes.
- Do not use advisory learning as a canonical decision without the separately authorized consumer edge.
- Do not make a successful weekly delivery contingent on availability of optional DATA PING or shadow sources.

## Integration and acceptance
- First identify existing weekly writer/workflow and its authorized output path. Add the audit as an output of that existing writer, without adding a workflow, cron, router, scheduler or autonomous merge.
- Preserve single-writer serialization and the existing SHA-256/readback process. Validate report bytes, schema, provenance, timestamps, week alignment, private/public boundary and consumer completeness independently.
- Run focused unit tests, corrupted-input negative tests, mutation-sensitive guard tests, and the existing weekly workflow test suite. Review exact diff, current governance and CI before merging.
- After an authorized merge, observe the **next natural weekly production run** and verify the exact on-main artifact, hash/readback and consumer receipt. No synthetic production success.
- Weekly summaries are evidence indexes, not source data; original frozen artifacts remain immutable.
