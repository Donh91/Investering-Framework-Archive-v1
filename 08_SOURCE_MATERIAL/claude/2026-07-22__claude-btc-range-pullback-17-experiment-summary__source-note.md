# Claude BTC Range and Pullback 17-Experiment Summary

**Dato:** 2026-07-22  
**Status:** SOURCE_NOTE / USER_PASTED_SUMMARY / NOT_INDEPENDENTLY_REPRODUCED  
**Område:** Claude Research Lab, BTC weekly ranges, pullback prediction, rebuy research  
**Primary folder:** `08_SOURCE_MATERIAL/claude/`  
**Related folders:** `06_RESEARCH_LAB/audit_summaries/`, `05_CYCLE_NAVIGATOR/forward_range_ledger/`, `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `05_CYCLE_NAVIGATOR/protocols/2026-07-08__forward-range-ledger-protocol-v0-1__canonical.md`, `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`, `01_CORE_FRAMEWORK/governance/2026-07-22__sensor-relationship-and-incremental-value-standard__canonical.md`

---

## 1. Source identity

```yaml
source_model: Claude / Fable
received_as: USER_PASTED_RESEARCH_SUMMARY
research_date_reported: 2026-07-22
raw_dataset_attached: false
raw_api_responses_attached: false
code_attached: false
parameter_registry_attached: false
full_result_tables_attached: false
request_ledger_attached: false
checksum_manifest_attached: false
independent_reproduction_completed: false
archive_role: SOURCE_NOTE_ONLY
```

No ZIP, executable notebook, source receipts or complete experiment output accompanied the pasted summary.

All numeric findings below are therefore recorded as:

```text
CLAUDE_REPORTED
NOT_REPRODUCED_BY_MAIN_FRAMEWORK
NOT_CANONICAL_TRUTH_LAYER
```

## 2. Claimed research design

Claude reports:

```text
Asset: BTC
History: approximately 2017-2026
Daily observations: 3,261
Weekly observations: 458
Primary data description: Binance mirror full history
Cross-check: Kraken
Median cross-source deviation: 0.031 percent
Train period: 2017-2023
Test period: 2024-2026
Experiments: 17
Additional fields: taker flow and trade count
```

The exact source endpoint, market symbol, quote currency, timezone, weekly-boundary convention, data-cleaning method and missing-observation policy were not supplied.

## 3. Claude-reported range findings

### 3.1 Baseline and width-only oracle

Claude reports:

```text
Naive symmetric ATR14 band, multiplier 1.25:
median Jaccard = 0.515

Perfect-width oracle:
median Jaccard = 0.624

Difference:
0.109 Jaccard points

Maximum result among 300 random parameter combinations:
0.006 above the stated reference noise floor
```

Claude interprets this as evidence that weekly range prediction is close to saturated and recommends freezing the range method near ATR14 x 1.25-1.50.

### 3.2 Centre tilt

Claude reports the following Jaccard results when the weekly band centre is shifted by a multiple of the previous week's return:

| Centre shift | Train | Test |
|---:|---:|---:|
| -0.50 | 0.443 | 0.456 |
| -0.25 | 0.482 | 0.481 |
| 0.00 | 0.512 | 0.518 |
| +0.25 | 0.482 | 0.493 |
| +0.50 | 0.428 | 0.457 |

Claude describes zero shift as the optimum in both train and test and concludes that momentum or mean-reversion drift tilt harms this specific band-centre construction.

### 3.3 Other range variants reported as unsuccessful

Claude reports that the following did not produce a durable improvement:

- volatility term structure as a width modulator;
- previous week's range as anchor;
- volume-conditioned width;
- adaptive width;
- asymmetric width;
- general downside skew.

Claude also reports that the preferred skew changed sign across market eras.

## 4. Claude-reported pullback and rebuy findings

### 4.1 Downside target

Target definition reported:

```text
Abnormal downside event:
BTC decline less than or equal to -3 x ATR14 percent within 10 days

Base rate:
13.2 percent
```

Reported feature lifts:

```text
ext20: 1.05x
atr_ts: 0.95x
tbr7: 0.95x
clv5: 0.88x
vol_r: 1.31x
ret5: 0.93x
churn: 1.05x
```

Claude interprets the clustering near 1.0 as no useful downside warning edge among the tested features.

### 4.2 Unconditional upside target

Claude reports stronger unconditional upside lifts:

```text
clv10: 1.96x
ret5: 1.96x
ext20: 1.89x
clv5: 1.84x
ext50: 1.75x
low atr_pct: 1.77x
```

The exact upside target is described as an abnormal rise greater than or equal to +3 x ATR14 percent within 10 days, with a base rate of 17.9 percent.

### 4.3 Pullback-conditioned rebuy test

When conditioned on BTC already being at least 10 percent below its 60-day high, Claude reports:

```text
Combined rebuy signal:
Train lift 0.94x
Test lift 0.99x

Mirrored bear signal:
Train lift 0.95x
Test lift 1.23x
```

Claude concludes that the unconditional upside effect did not survive in the actual pullback state and that the tested bottom-catching construction had no edge.

## 5. Claude-reported volatility-compression finding

Claude reports a test-period sample of 28 pullback observations with volatility compression:

```text
Binary lift: 1.85x
Median forward 10-day upside: +1.15 percent
Median forward drawdown: -13.62 percent
Payoff ratio: 0.08
Reported base payoff ratio: 1.15
```

Claude uses this as an example of a high hit-rate metric hiding an adverse outcome distribution.

The pasted summary also reports the following current-state measurements as settled on 2026-07-21:

```text
180-day volatility percentile: 19 percent
ATR7 / ATR14: 0.929
Distance from 60-day high: -14.76 percent
```

These current-state values were not accompanied by source receipts and are not promoted into a live alert or framework state.

## 6. Claude's proposed conclusions

Claude recommends:

1. freeze weekly range width near symmetric ATR14 x 1.50 around the previous weekly close;
2. use no centre tilt, adaptive width or directional skew;
3. treat pullback protection as reactive risk management rather than predictive warning;
4. follow confirmed strength for rebuy rather than trying to catch bottoms;
5. require median forward upside and median forward drawdown beside every hit-rate claim;
6. preserve the current low-volatility pullback configuration as a caution flag;
7. leave current classification, Stage-1 and rebuy lock unchanged.

## 7. Provenance and reproducibility limitations

The following are unresolved:

```text
EXACT_PRIMARY_SOURCE: UNKNOWN
EXACT_MARKET_SYMBOL: UNKNOWN
QUOTE_CURRENCY: UNKNOWN
TIMEZONE_AND_WEEK_BOUNDARY: UNKNOWN
CANDLE_SETTLEMENT_RULE: UNKNOWN
BINANCE_MIRROR_CONSTRUCTION: UNKNOWN
KRAKEN_CROSSCHECK_METHOD: UNKNOWN
TAKER_FLOW_FIELD_SEMANTICS: UNKNOWN
TRADE_COUNT_FIELD_SEMANTICS: UNKNOWN
MISSING_DATA_POLICY: UNKNOWN
OUTLIER_POLICY: UNKNOWN
SURVIVORSHIP_AND_LISTING_POLICY: UNKNOWN
ATR_IMPLEMENTATION_DETAILS: INCOMPLETE
ORACLE_DEFINITION: INCOMPLETE
RANDOM_SEARCH_PARAMETER_SPACE: UNKNOWN
MULTIPLE_TESTING_CORRECTION: NOT_DOCUMENTED
BOOTSTRAP_OR_CONFIDENCE_INTERVALS: NOT_PROVIDED
TRANSACTION_COSTS: NOT_PROVIDED
ALL_17_EXPERIMENT_ROWS: NOT_PROVIDED
CODE_AND_ENVIRONMENT: NOT_PROVIDED
```

The claimed maximum from 300 random parameter combinations is not, by itself, a formal family-wise multiple-testing correction or a proof of a universal noise floor.

## 8. Source disposition

```text
SOURCE_ARCHIVE: ACCEPT
NUMERIC_TRUTH_LAYER: REJECT_PENDING_REPRODUCTION
OFFICIAL_FRLP_ROW: NOT_CREATED
OFFICIAL_RANGE_METHOD_CHANGE: NOT_AUTHORIZED
CURRENT_CAUTION_ALERT: NOT_AUTHORIZED
NEW_ENGINE_OR_TEST: NOT_AUTHORIZED
PORTFOLIO_AUTHORITY: ZERO
```

The durable value of this source is its negative-result hypothesis set and its challenge to metric design. Its numerical conclusions remain Claude-reported until an executable and independently reproducible package exists.
