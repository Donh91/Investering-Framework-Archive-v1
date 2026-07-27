# SOURCE_QA — preliminary backtest contract mismatches in Claude megapack

```yaml
incident_id: SOURCE_QA_BACKTEST_MEGAPACK_CONTRACT_MISMATCHES_20260727
source_package_sha256: 303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f
severity: HIGH
failure_class: TEST_IMPLEMENTATION_DOES_NOT_MATCH_DECLARED_HYPOTHESIS
caught_before_framework_execution: YES
canonical_harm_observed: NO
portfolio_harm_observed: NO
status: OPEN_REWRITE_AND_REGRESSION_REQUIRED
```

## Summary

The underlying data archive is high value. The preliminary test code must not be promoted because several implementations diverge from their declared contracts.

## Load-bearing findings

| Test | Finding | Required repair |
|---|---|---|
| BT01 | Session ETF features are reindexed to calendar days, forward-filled and shifted one calendar day. Samples inflate above real session counts. | Join each completed ETF session once using explicit `knowledge_time_utc`; measure outcomes from the first eligible timestamp only. |
| BT02 | Declared READY, but no preliminary BT02 result is generated. | Implement the preregistered reversal contract and fixtures. |
| BT03 | Trigger only checks three positive ETH/BTC increments. Leadership and breadth/dominance requirements are omitted. | Implement exact frozen condition set and direct-pair settlement basis. |
| BT04 | Simple gate-cross event returns are calculated, but the complete early-improvement, later-gate and failure-path contract is not frozen. | Preregister event, settlement basis, censoring and failure definitions. |
| BT05 | Uses one-day BTC loss below -8% and fixed delays. Framework confirmation gates, overlapping-event controls and state locks are absent. | Implement the actual rebuy-state machine and event deduplication. |
| BT06 | Uses funding z-score regimes only. OI state is omitted. | Cross funding and OI regimes with venue-specific availability rules. |
| BT07 | Measures unconditional ETH/BTC returns by breadth tercile rather than signal performance conditional on breadth. | Condition a frozen ETH/BTC signal on point-in-time breadth states. |
| BT08 | 2M bars are timestamped at bar start and results are measured from bar start, before settlement. | Move knowledge time and event time to bar settlement; exclude current incomplete bar. |
| BT09 | Calculates change between consecutive Sundays, not weekend movement versus next completed ETF session. | Join Friday or weekend crypto path to the next completed US ETF print without synthetic weekend zeros. |
| BT10 | No forecast, threshold, decision or framework-state ledger is present. | Ingest frozen point-in-time ledgers before replay. |

## Concrete diagnostic evidence

```yaml
BTC_ETF_session_rows: 651
BT01_reported_BTC_sample_n: up_to_925
ETH_ETF_session_rows: 513
BT01_reported_ETH_sample_n: up_to_731
BT09_actual_code_target: CONSECUTIVE_SUNDAY_BTC_PCT_CHANGE
BT08_actual_event_timestamp: TWO_MONTH_BAR_START
BT08_required_tradable_timestamp: TWO_MONTH_BAR_END
```

## Governance response

```yaml
raw_data_quarantine: NO
preliminary_result_quarantine: YES
backtest_execution_permission: NO
readiness_labels_from_source_package: NON_GOVERNING
required_before_execution:
  - frozen_test_contracts
  - corrected_builders
  - deterministic_regression_fixtures
  - point_in_time_checks
  - independent_code_review
  - explicit READY_FOR_CONTROLLED_BACKTEST_EXECUTION gate
```

No result in the package may alter a framework rule, sensor weight, forecast score, market state or portfolio decision.