# P8 TEST REPORT

Date: 2026-08-09
Implementation PR: #338
Implementation head: `0a73e2ef5a1cb3cab4240ad79963e302a20e7158`
Implementation merge commit: `904c61d3908efa6f1209c7286dda04bc06603fa3`

## Scope

Tests validate implementation and reliability only. Gate 0-B2 was not run. No Full-vs-Reduced agreement, divergence, outcome, reverse-ablation, economic ranking or winner selection was calculated.

## Deterministic blinded-collection regression tests

`tests.backtest_engine.test_blind_dual_run_v2` passed all 10 recovery-specific tests:

1. the five Gate 0-F eligible timestamps occupy exactly one fixed Unix-epoch 72h window;
2. dense four-hour observations across 13 weeks occupy at least 30 fixed windows and span at least 12 weeks;
3. continuous observations cannot collapse transitively into one single-linkage cluster;
4. Full and Reduced use the same T and exact same capture hash, with exact profile counts 32 and 18;
5. no future Minimal artifact is emitted;
6. rotation uses the native fail-closed path with missingness preserved and `imputation=false`;
7. REBUY and TRIM are not synthesized when native profile outputs are absent;
8. collection artifacts contain no comparison metrics;
9. the coverage monitor still works if profile child policy files are made unreadable, proving it reads pair receipts only;
10. repeated processing of the same capture is idempotent.

## GitHub Actions evidence

PR #338 triggered nine workflows. All nine completed `success`:

- Storage Health Gate, run `31311616350`
- Full Architecture 1-7 Gate, run `31311616326`
- Backtest Wave 1.4 Prospective Accumulation, run `31311616358`
- Daily Capture Architecture Gate, run `31311616385`
- Backtest Wave 1.2 Foundation, run `31311616356`
- Automation Production Health Gate, run `31311616383`
- Backtest Engine Foundation, run `31311616351`
- Data Architecture Gate, run `31311616335`
- Continuity Learning Gate, run `31311616364`

### Backtest Wave 1.4

The job `validate-prospective-foundation` completed successfully.

The combined old prospective foundation tests plus the new blinded collection tests ran 18 tests and returned `OK`.

The active v1 validation reported:

```json
{"comparison_metrics_calculated": false, "structure": "PASS", "v1_run_groups": 5}
```

The v2 metadata-only audit reported:

```json
{
  "b2_analysis_authorized": false,
  "comparison_metrics_calculated": false,
  "coverage_contract": "PROSPECTIVE_B2_COVERAGE_WINDOWS_v1",
  "engineering_status": "PASS_ACTIVE",
  "paired_receipt_count": 0
}
```

The zero paired-receipt count is expected at PR-test time because the implementation deliberately did not manufacture a historical v2 row and did not manually invoke the live market-data workflow.

### Daily Capture Architecture Gate

The `gate` job ran 15 tests and returned `OK`, then compiled all modified capture modules and returned:

`DAILY_CAPTURE_AND_BLINDED_DUAL_RUN_ARCHITECTURE_PASS`

The separate `live-hourly-source-smoke` job also completed successfully without writing repository state.

Static assertions confirmed:

- exactly five pre-existing Copenhagen live-anchor schedules remain;
- exactly two pre-existing hourly-sequence schedules remain;
- the v2 collector is wired exactly once;
- no `OPENAI_API_KEY` is introduced into the new path;
- the new collector contains no HTTP/network client dependency;
- the new collector does not call legacy `score_shadow_period`;
- Legacy Minimal is explicitly excluded;
- current storage and market-data endpoint boundaries remain unchanged.

## Changed-path audit

PR #338 changed exactly 13 files, restricted to:

- three workflow files;
- one new collector module;
- one new runtime wrapper;
- one new test module;
- P1 through P7 implementation/research artifacts.

It did not change:

- `SENSOR_ROLE_DEPENDENCY_REGISTRY_v1.json`;
- `POLICY_FAMILY_REGISTRY_v1.json`;
- `SEQUENTIAL_RESEARCH_QUEUE_v1.json`;
- `backtest_engine/rotation.py`;
- v1 dual-run contract or ledger;
- any market rule, threshold, weight or policy semantics.

## Baseline health note

The repository-wide production-health dashboard was already RED before this task because of unrelated existing PDLT/weekly workflow failures and staleness. That baseline was not reclassified or hidden. The PR-level Automation Production Health Gate nevertheless passed, and all recovery-relevant PR checks were green before merge.

## Test verdict

`PASS_IMPLEMENTATION_AND_BLINDING_GATES`
