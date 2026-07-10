# TechDev Topping Signals Updates #1–#8 — Historical Extraction

**Import date:** 2026-07-10  
**Status:** HISTORICAL_SOURCE_BACKED_SEQUENCE / UNSCORED  
**Authority:** HISTORICAL_CONTEXT_ONLY  
**Related ledger:** `2026-07-10__techdev-claim-ledger__operational.md`  
**Source manifest:** `08_SOURCE_MATERIAL/techdev/2026-07-10__techdev-topping-signals-updates-1-8__source-manifest.md`

## Purpose

Preserve the evolution of TechDev's four topping signals without turning old indicator commentary into current framework doctrine.

The four signals were:

1. Top Gauge
2. Tether Dominance monthly RSI trend line
3. Bitcoin weekly Bollinger Band Width
4. Pi Cycle Top cross

## Historical snapshot rows

| Update/date | Top Gauge | Tether Dominance RSI | Bollinger Band Width | Pi Cross | TechDev interpretation | Status |
|---|---|---|---|---|---|---|
| #1 / 2024-01-22 | NOT_TRIGGERED; displayed 77 | NOT_TRIGGERED | NOT_TRIGGERED | NOT_TRIGGERED | Initial weekly monitoring sequence | SOURCE_BACKED_UNSCORED |
| #2 / 2024-02-04 | NOT_TRIGGERED; displayed 87 | NOT_TRIGGERED | NOT_TRIGGERED | NOT_TRIGGERED | No top signal active | SOURCE_BACKED_UNSCORED |
| #3 / 2024-02-19 | NOT_TRIGGERED; displayed 92 | NOT_TRIGGERED | NOT_TRIGGERED | NOT_TRIGGERED | No top signal active | SOURCE_BACKED_UNSCORED |
| #4 / 2024-03-03 | NOT_TRIGGERED; displayed 96; described as getting hot | NOT_TRIGGERED; getting hot | NOT_TRIGGERED | NOT_TRIGGERED | A 2-week close at/above the threshold would prompt de-risking; historical lead from 96 was described as 2–20 weeks | SOURCE_BACKED_UNSCORED |
| #5 | DATA_MISSING | DATA_MISSING | DATA_MISSING | DATA_MISSING | SOURCE_MISSING | NOT_EVALUABLE |
| #6 / 2024-03-31 | CALLED_TRIGGERED despite falling just short of 100 | NOT_TRIGGERED; very hot | NOT_TRIGGERED | NOT_TRIGGERED | TechDev used other indicators and context to classify Top Gauge as triggered at subwave 3 top | SOURCE_BACKED_UNSCORED |
| #7 / 2024-04-14 | TRIGGERED maintained | NOT_TRIGGERED | NOT_TRIGGERED | NOT_TRIGGERED | Expected subwave 5 into a first top while Top Gauge temporarily reversed and then declined | SOURCE_BACKED_UNSCORED |
| #8 / 2024-05-20 | UNCERTAIN; TechDev stated that if the gauge held above 60 he no longer believed 96 was an actual trigger | NOT_TRIGGERED; very hot | NOT_TRIGGERED | NOT_TRIGGERED | Trigger interpretation was revised and made scenario-dependent | SOURCE_BACKED_UNSCORED |

## Source-backed observations

### 1. Mechanical versus discretionary trigger

The available sequence shows that the displayed Top Gauge did not reach its stated 100 threshold in Update #6, yet TechDev classified it as triggered using surrounding indicators and market interpretation.

```text
MECHANICAL_THRESHOLD_HIT: NO_OR_NOT_DOCUMENTED
ANALYST_OVERRIDE: TRIGGERED
```

This distinction must remain visible in any later calibration.

### 2. Trigger revision

Update #8 did not silently erase the earlier trigger call. It reclassified the signal as uncertain and stated that a hold above 60 would imply the earlier 96 reading was not an actual trigger.

```text
EARLIER_CALL: TRIGGERED
LATER_STATUS: UNCERTAIN
RETROSPECTIVE_ERASURE: FORBIDDEN
```

### 3. Cross-signal confirmation was absent

Across the seven available snapshots, Tether Dominance RSI, Bollinger Band Width and Pi Cross were never marked triggered. The sole active call was the discretionary Top Gauge classification in Updates #6 and #7.

This does not determine whether the market call was right or wrong. It shows that the call lacked confirmation from the other three named topping signals.

### 4. Scenario dependence increased over time

By Update #8, expected signal behavior differed across three market scenarios. This is useful historical evidence but also makes ex-post interpretation easier unless the scenario was frozen before the outcome.

## Provisional framework relevance

```yaml
current_operational_rule_change: NONE
historical_learning_candidate:
  - separate mechanical reading from analyst override
  - preserve later downgrade without erasing earlier call
  - require frozen scenario and trigger definition before scoring
  - do not count three non-triggered signals as confirming a top
promotion_status: NOT_PROMOTED
scoring_status: BLOCKED
```

## Missing evidence before outcome scoring

1. Topping Signals Update #5.
2. Market Update Issue #35 Part 2 for the original Top Gauge definition.
3. Market Update Issue #26 Part 1 for the other three indicator definitions.
4. Market Update Issue #42 for the surrounding March 2024 market thesis.
5. A frozen actuals/scoring method defining what counts as a useful top warning, false positive, lead time and action value.

## Boundary

This extraction is historical calibration input only. It does not reactivate any old threshold, indicator or two-top thesis in the current framework.
