# AT-EXP-004 bounded implementation checkpoint

Date: 2026-09-13
Status: IMPLEMENTED_PENDING_INDEPENDENT_REVIEW_AND_MERGED_READBACK
Owner: issue #941; Codex candidate codex-research-at-exp-004-bounded-remediation-closure-v1
Base: 9e2a1e2325bb20ae67ecf5f7f538d0e5947d3c05

## Delivered slice

Removed the current-open fallback from closed one-hour returns. Missing state inputs produce an empty derived state. Hourly persistence uses the categorical predicate specified in #941: PASS source statuses plus finite BTC/ETH derived inputs and matching states. A PASS retry upgrades DEGRADED; otherwise the existing same-interval record wins because this owner has no real detection timestamp. No scalar quality score. Situation Room retains PASS over DEGRADED and requires a later valid timezone-aware detection time for equal-quality replacement. Rejected attempts are hash-keyed, deduplicated metadata under each owner's superseded directory and do not enter Situation Room's event ledger or latest pointer.

## Evidence and limits

The four new synthetic composition tests fail on the original base (five subtest failures, zero errors) and pass on the candidate. The focused producer/persistence, hourly measurement, pipeline, Situation Room owner and static adapter suite passes 51 tests. Replay compares all common market fields for every-bar vs every-sixth-bar schedules; only source_window_end_utc is excluded, as declared in the test docstring before execution. Source raw field computation is unchanged. The directional summary now truthfully reports 25 eligible returns from a 26-candle fixture lacking a preceding close.

A broader daily_capture discovery ran 114 tests with one unrelated CFGI workflow-string expectation failure and one missing-pytest import error. Those paths were not changed. Do not report all repository tests green.

Original external AT-EXP-004 package and its detector pin are referenced in issue #941 but were not present at the experiment path on this base. This checkpoint preserves a new implementation test result, not the original external experiment or a retroactive rescore. Do not claim the reported 867-row census or 157 damaged states were rerun here.

## Quarantine and next single work item

Keep AUTO_TRADING alpha research blocked. Intraday execution research reads hourly return_1h_pct and oi_change_1h_pct (scripts/intraday_execution/intraday_execution_research_core.py), so its historical derived evidence remains exposed. Pullback's hourly consumer reads btc_close, eth_close and ethbtc_close only; its raw-price lane remains outside this specific defect. Situation Room remains pending final writer/readback proof. No historical CSV or ledger was changed and no reconstruction sidecar was fabricated.

Next executor: independently review this exact candidate, rerun the focused command, check integration against fresh main and required CI, then merge only through the existing review gate. Recover/bind the original research package before claiming full #941 closure. Re-evaluate quarantine on the exact merged commit; preserve old rows and use an explicit hash-bound sidecar only if justified. Publish the existing completion/convergence receipts only after every owner acceptance item is satisfied. Do not restart implementation or add a new queue owner.

Command:
python -B -m unittest tests.daily_capture.test_at004_persistence tests.daily_capture.test_daily_capture_pipeline tests.daily_capture.test_audit_hourly_measurements tests.data_terminal.test_situation_room_daily_owner tests.data_terminal.test_situation_room_static_daily_adapter -q

## Low-cost takeover

Work quota telemetry is unavailable. No paid API call was made. Existing API_TASK_REGISTRY_v1 admits research/review output only, while CAPABILITY_ROUTING_POLICY_v1 routes code writes to CODEX_ONLY. A Sol API reviewer can inspect this bounded package through an admitted research task, but is not currently a verified autonomous code/merge executor. API execution was not queued or claimed. The durable Codex transition and PR remain the executable handoff; do not change budget or authority to manufacture fallback capability.

## CI-discovered composition correction

The first candidate failed Situation Room live CI with KeyError retrieval: owner.run wrote a preliminary record before the static adapter applied final failure semantics and metadata, then the new equal-time guard rejected the final write. owner.run now returns an unpersisted candidate; the existing static adapter performs its one final write, and the direct CLI explicitly writes its result. Repository caller search found the static adapter as the sole production caller of owner.run. An additional real-adapter/mocked-fetch regression verifies exactly one write, persisted retrieval metadata, and preservation of final DEGRADED status. This correction stays in the allowed owner file and adds no workflow or adapter changes.
