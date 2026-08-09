# P1 CURRENT DUAL RUN AUDIT

Date: 2026-08-09
Repository: Donh91/Investering-Framework-Archive-v1
Authoritative starting HEAD: `38942f22f715cd64291755cf2050642aa261749a`

## Scope

This audit is limited to prospective paired evidence recovery. Gate 0-B2 was not executed. No Full-vs-Reduced agreement, divergence, outcome, reverse-ablation or economic ranking was calculated.

## Frozen identities revalidated

- FULL_STACK: exact current 32 non-retired sensors in `SENSOR_ROLE_DEPENDENCY_REGISTRY_v1`.
- REDUCED_EXECUTION_STACK: exact frozen 18-sensor list in the same registry.
- LEGACY_MINIMAL: `EXCLUDED_UNRECOVERABLE`; historical v1 Minimal rows remain immutable.
- Native policy families present: `REBUY_LOCK`, `NEW_ENTRY_PERMISSION`, `TRIM_NO_TRIM`, `ROTATION_PERMISSION`.
- Gate 0-E primary collection surface remains ROTATION_PERMISSION, REBUY_STATE through native REBUY_LOCK only, and TRIM_EXIT_STATE through native TRIM_NO_TRIM only.
- BTC_PERMISSION, ECOSYSTEM_PERMISSION and RISK_STATE remain excluded because no admissible frozen evaluators exist.

## v1 trace and stop cause

`SHADOW_SIMPLIFICATION_DUAL_RUN_v1.json` was added by commit `1e42767813b831ceec68409d62135c2f70dc3f20`.
`RUN_LEDGER_v1.json` was initialized by commit `8b5bb74dc637cd946b90cc555776fcf7b731ecd6`.
The five prospective run groups were then appended by direct ledger commits beginning with `85fefa11e6544e9a7b5518687c943b77d0c01210` and ending 2026-07-29. The scheduled `backtest-wave1-4-prospective.yml` has read-only repository permission and only validates/audits existing ledgers. It does not create dual-run rows. No recurring workflow was found that materialized v1 paired rows from capture automation.

Primary cause classification: `LEGACY_MANUAL_ONLY`.
Direct runtime mechanism: `WORKFLOW_NOT_WIRED`.
Later architecture change: the 2026-08-08 two-lane capture architecture superseded snapshot-only collection, but it did not wire v1 dual-run materialization.

## Current capture architecture

The current live data architecture has:
- `Daily Live Anchor Capture`, five scheduled PIT anchors per Europe/Copenhagen day.
- `Hourly Sequence Capture`, two scheduled materializations per day, retaining completed hourly sequence memory.
- current live-anchor contract `DAILY_LIVE_ANCHOR_INDEX_v3`.
- live anchors are shadow-only, non-binding, no portfolio action, no framework state change.
- current automation can be reused without adding a new market-data collector or increasing source-call cadence.

Safest integration point: immediately after the existing compact live-anchor index is built, before the workflow's existing atomic commit/rebase/push block.

## Native evaluator audit

ROTATION_PERMISSION:
- native executable path proven: `backtest_engine/rotation.py::classify_rotation`.
- native fail-closed behavior is explicit.
- Gate 0-F already treated the native fail-closed or present-input path as admissible.

REBUY_STATE:
- policy family `REBUY_LOCK` exists.
- the five v1 prospective rows contain native rebuy output.
- no separate generative rebuy evaluator was proven in the current code audit.
- v2 therefore copies REBUY only when an explicit profile-native `REBUY_LOCK` output already exists at T; otherwise `POLICY_OUTPUT_UNAVAILABLE`.

TRIM_EXIT_STATE:
- family and label crosswalk exist.
- no current native profile-specific TRIM_NO_TRIM evaluator/output path was proven.
- v2 therefore records `POLICY_OUTPUT_UNAVAILABLE` and never synthesizes trim.

## Queue and budget

`SEQUENTIAL_RESEARCH_QUEUE_v1` remains `ACTIVE_SHADOW_ONLY` with:
- `one_active_execution_stage_only = true`
- `passive_maturation_may_overlap = true`
- `cfgi_credits_hard_cap = 0`
- `openai_usd_hard_cap = 0.0`

The active stage list is not modified.

## Baseline automation health

The repository-wide automation health was already RED before this implementation due unrelated existing failures/staleness, including PDLT discovery and weekly jobs. The capture lane itself was functioning: recent `daily-raw-owner-capture.yml` and `hourly-sequence-capture.yml` runs were GREEN. This task must not hide or reclassify unrelated baseline failures.

## Implementation admissibility verdict

The passive collection wiring can be implemented without changing market rules, thresholds, weights, gates, portfolio authority or policy semantics. v1 remains untouched. v2 uses metadata-only monitoring and stores profile outputs in separate immutable child artifacts.
