# BACKTEST BUILD extension audit — TDBC v1 TechDev Business Cycle

**Source timestamp:** 2026-07-26T21:32:00Z  
**Audit status:** `PACKAGE_INTEGRITY_PASS / METHOD_IDENTIFICATION_HIGH_VALUE / FULL_REPRODUCIBILITY_INCOMPLETE / TEST_EXECUTION_LOCKED`  
**Program:** `FRAMEWORK_BACKTEST_READINESS_BUILD_v1`  
**Authority:** source QA, research inventory and future test design only.

## 1. Governance decision

```yaml
archive_now: YES
raw_source_identity: PRESERVED_BY_HASH_AND_INVENTORY
independent_backtest_execution: NO
indicator_reconstruction_execution: NO
sensor_ratification: NO
falsifier_ratification: NO
forecast_creation: NO
FNP_prior_change: NO
rotation_or_portfolio_effect: NONE
canonical_state_change: NONE
```

The package is a major research extension because it turns the TechDev business-cycle chart from a visual analogy into a concrete candidate specification. It does not unlock test execution or establish economic edge.

## 2. Supplied artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `TDBC v1 TechDev Business Cycle 2026-07-26.zip` | 237,291 | `e83d3b95e94fba331767feae92bd052ed7f752a1a5305d63621030b293bc5d4c` |
| TechDev chart image | 152,750 | `5b9691af6456ae1148eac7c42897a757c67fa326ca83a0b0875d17850a31af51` |

ZIP structure:

```yaml
zip_members: 18
uncompressed_bytes: 786311
checksum_ledger_entries: 17
checksum_mismatches: 0
missing_checksum_targets: 0
```

The checksum ledger correctly covers every package member except the checksum ledger itself. The README text says checksums cover 16 files, while the actual ledger covers 17. This is a minor documentation count defect, not a payload-integrity defect.

## 3. Verified package contents

### Current-run objects

- one main report;
- one Python indicator-reconstruction script;
- 157 two-month histogram rows;
- 25 event-forward-return rows;
- five proposed falsifier rows;
- six zero-cross discriminator rows;
- six source-data tables.

### Source data coverage

| Dataset | Rows | Coverage |
|---|---:|---|
| COMEX copper daily | 6,503 | 2000-08-30 to 2026-07-24 |
| COMEX gold daily | 6,498 | 2000-08-30 to 2026-07-24 |
| BTC daily | 5,852 | 2010-07-18 to 2026-07-25 |
| ETH daily | 4,005 | 2015-08-08 to 2026-07-25 |
| FRED copper monthly | 414 | 1992-01-01 to 2026-06-01 |
| LBMA gold monthly | 2,322 | 1833-01 to 2026-06 |

No duplicate date keys were found in these six source tables.

### Prior-run replication objects

The package contains a second, earlier calculation chain with:

- 157 indicator rows;
- 25 event rows;
- 96 phase rows;
- 36 sensitivity-grid rows.

All 157 current-run histogram rows align to the prior-run rows by bar-close date. Differences in copper/gold, MACD and histogram values are rounding-level only. This is useful replication evidence, but both runs remain within the same research package and are not equivalent to a framework-owned independent reproduction.

## 4. Candidate method identification

Package-proposed specification:

```yaml
series: COPPER_DIVIDED_BY_GOLD
bar_interval: 2_MONTH
anchor: JAN_FEB_MAR_APR_SEQUENCE
indicator: MACD_12_26_9
plot: MACD_HISTOGRAM
current_bar: IN_PROGRESS_SETTLES_2026-08-31
```

The existing TechDev archive independently supports that the framework uses the **2-month Copper/Gold MACD histogram** and a separate **2-month Copper/Gold RSI**. The exact default parameters, anchor convention and ticker implementation are not independently established by the current framework archive.

Correct classification:

```yaml
broad_indicator_identity: CORROBORATED
exact_12_26_9_parameterization: HIGH_CONFIDENCE_CANDIDATE
jan_feb_anchor_convention: HIGH_CONFIDENCE_CANDIDATE
exact_techdev_ticker_pair: UNRESOLVED
canonical_sensor_spec: NOT_RATIFIED
```

## 5. Settlement finding

The packaged series distinguishes:

```yaml
last_settled_bar_end: 2026-06-30
last_settled_histogram_e5: -1.61246429
current_bar_end: 2026-08-31
current_bar_histogram_e5: 0.49053007
current_bar_status: IN_PROGRESS_2M
```

Therefore the displayed positive bar cannot be admitted as a settled macro state. It may remain a visual urgency observation only.

The package also reports current-sign sensitivity to source and anchor conventions. This strengthens the requirement that a future canonical sensor must freeze:

- source owner;
- ticker convention;
- bar anchor;
- settlement time;
- revision handling;
- partial-bar display rules.

## 6. Static code audit

`TDBC_INDICATOR_SPEC_v1.py`:

```yaml
python_syntax: PASS
indicator_formula_present: YES
partial_bar_labeling_present: YES
source_receipt_hashing_present: YES
```

Important reproducibility gaps:

1. The script always downloads Yahoo source data and has no implemented offline mode, despite the package containing local raw tables and describing offline reproducibility.
2. Dependencies are not version-pinned.
3. The script reconstructs the indicator and phases only. It does not rebuild:
   - event-forward-return tables;
   - block-bootstrap statistics;
   - gold-frozen counterfactuals;
   - BTC-top alignment;
   - ETH/BTC transmission tables;
   - falsifier table;
   - source-B comparison;
   - sensitivity grid.
4. The script does not independently consume the packaged FRED, LBMA, BTC or ETH files.
5. Raw HTTP response bytes are represented by receipts, but are not themselves included.

Consequently:

```yaml
indicator_reconstruction_reproducibility: PARTIAL
full_report_reproducibility: FAIL_INCOMPLETE_CODE
package_claim_self_contained_offline: NOT_CURRENTLY_IMPLEMENTED
replay_safe_builder_status: NOT_READY
```

## 7. Research findings retained as unratified hypotheses

The following are archived as package claims and future hypotheses, not framework conclusions:

- unsettled zero-cross may occur on 2026-08-31;
- the current ratio move may be materially gold-confounded;
- confirmation delay may reduce subsequent return capture;
- ETH/BTC transmission speed may discriminate true versus false macro turns;
- BTC-top versus histogram-top alignment may define a future falsification window;
- the 2023 positive bar is a visually hidden false start;
- four proposed discriminator/falsifier rules may be useful for controlled testing.

The package itself reports only four independent forecast events and a best block-bootstrap result around `p = 0.17`. It correctly labels the evidence descriptive rather than inferential.

## 8. Proposed falsifiers

`TD-F1` through `TD-F5` are preserved as `UNRATIFIED_RESEARCH_PROPOSALS`.

They are not active Forecast Ledger rows because:

- the final test matrix is not ratified;
- the owner-source and settlement contracts are not frozen;
- some statements were derived after reviewing historical outcomes;
- test execution is locked;
- no current framework forecast should be created from an unadmitted research package.

## 9. Readiness contribution

The package materially advances these future workstreams:

```yaml
BT08_BUSINESS_CYCLE_TURN:
  prior_status: BLOCKED_MISSING_NUMERICAL_SPEC
  new_status: CANDIDATE_SPEC_AND_DATA_RECEIVED_REPRODUCTION_REQUIRED

TECHDEV_SENSOR_REVERSE_ENGINEERING:
  status: HIGH_VALUE_EXTENSION

GOLD_CONFOUND_DECOMPOSITION:
  status: CANDIDATE_TEST_DESIGN_RECEIVED

ETHBTC_TRANSMISSION_TEMPO:
  status: CANDIDATE_TEST_DESIGN_RECEIVED
```

It does not move any workstream to `READY`.

## 10. Required repair package before controlled testing

A framework-owned builder must eventually:

1. run solely from locked local source files;
2. pin Python and dependency versions;
3. rebuild every report table, not only the indicator;
4. generate detached receipts and schema checks;
5. separate settled and in-progress bars;
6. run both source conventions and both anchor conventions;
7. preserve copper and gold leg contributions separately;
8. implement point-in-time event joins;
9. exclude or separately label non-tradable early BTC regimes;
10. produce out-of-sample or forward-only evaluation rules.

## 11. Final disposition

```yaml
source_archive: ACCEPTED
binary_identity: PASS
internal_checksums: PASS_17_OF_17
method_identification_value: HIGH
broad_techdev_alignment: CORROBORATED
exact_algorithm_ratification: NO
current_positive_cross: UNSETTLED_NOT_ADMISSIBLE
full_backtest_reproducibility: INCOMPLETE
statistical_edge_claim: NONE
TD_F1_TO_TD_F5: UNRATIFIED
sensor_promotion: NO
backtest_execution: LOCKED
framework_state_change: NONE
portfolio_action: NONE
next_gate: RECEIVE_REMAINING_PACKAGES_AND_BUILD_FRAMEWORK_OWNED_REPRODUCTION_SPEC
```
