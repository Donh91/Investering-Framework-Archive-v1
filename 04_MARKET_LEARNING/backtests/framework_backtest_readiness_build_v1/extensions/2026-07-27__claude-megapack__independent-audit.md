# BACKTEST BUILD independent audit — Claude multi-source megapack

**Artifact:** `DATA PING BACKTEST HISTORY PACK 20260727T052808Z.zip`  
**Generated upstream:** 2026-07-27T05:28:53Z  
**Program state:** `HISTORICAL_DATA_ACCUMULATION / TEST_EXECUTION_LOCKED`  
**Audit verdict:** `DATA_ARCHIVE_HIGH_VALUE / PAYLOAD_INTEGRITY_PASS_WITH_SCOPE_NOTE / PRELIMINARY_TEST_OUTPUTS_QUARANTINED`

## 1. Package identity and integrity

```yaml
bytes: 190546648
sha256: 303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f
zip_members_total: 214
regular_files: 183
directory_entries: 31
payload_files_listed_in_manifest: 180
checksum_entries: 180
checksum_mismatches: 0
checksum_missing_targets: 0
```

All 180 payload files listed in `CHECKSUMS.sha256` match exactly. The upstream statement that every ZIP member carries a checksum is too broad: `README.md` and `manifest.json` are outside the detached checksum ledger, while `CHECKSUMS.sha256` naturally cannot self-hash. Their independently calculated hashes are:

```yaml
README_md_sha256: 41677523791ccdc58b249ac02cdb6076a34b91e5c5fb4cde5ffc07f7aca041cf
manifest_json_sha256: 4decdbe1f9f66166a59322c819a303cc65657cde8e7307b941f44dc7d861672d
CHECKSUMS_sha256_file_hash: 0d2a2e4aee7a0e2caf236b84064e5fb9413f3d2444b4ee53de08df71ec15e465
```

This is an inventory-scope clarification, not evidence of payload corruption.

## 2. Independently reproduced inventory counts

The following row counts were verified directly from the packaged CSV or CSV.GZ files without executing the supplied collectors or backtest scripts:

| Family | Verified rows | Verified coverage / entities |
|---|---:|---|
| CoinMetrics asset metrics | 1,405,137 | 838 assets, 2009-01-03 through 2026-07-26 |
| Binance USDT universe | 777,567 | 623 symbols, 2017-08-17 through 2026-07-26 |
| Yahoo macro daily long | 330,427 | 60 instruments, 2001-07-23 through 2026-07-26 |
| Master daily panel | 5,852 | 2010-07-18 through 2026-07-25 |
| Point-in-time breadth | 3,266 | 2017-08-17 through 2026-07-26 |
| Cross-venue parity | 13,041 | three assets, 2011-08-18 through 2026-07-26 |
| BTC normalized daily | 3,266 | 2017-08-17 through 2026-07-26 |
| ETH normalized daily | 3,266 | 2017-08-17 through 2026-07-26 |
| Direct ETH/BTC normalized daily | 3,300 | 2017-07-14 through 2026-07-26 |
| TechDev reconstruction, Jan-Feb anchor | 151 | bar starts 2001-07-26 through 2026-07-01 |
| BT08 daily state output | 5,852 | 2010-07-18 through 2026-07-25 |

The ETF feature table contains 651 BTC sessions and 513 non-null ETH sessions, with zero weekend rows. The raw-data breadth is materially valuable and removes several prior historical-data blocks.

## 3. Data-family value

The package materially improves future readiness for:

- direct historical ETH/BTC gate and transmission research;
- BTC and ETH spot price history at multiple frequencies;
- derivatives funding, basis, OI and ratio studies;
- survivorship-aware Binance breadth using delisted symbols;
- ETF-flow joins;
- cross-venue parity and source-break analysis;
- CoinMetrics on-chain and market-cap panels;
- sentiment, stablecoin and TVL research;
- TechDev Copper/Gold reconstruction research.

The FRED family remains absent. Yahoo and DBnomics proxies do not replace point-in-time FRED vintages or FRED-only series.

## 4. TechDev specification treatment

The package provides a complete reconstruction formula and implementation:

```yaml
signal_1_candidate: MACD_12_26_9_OF_COPPER_GOLD_ON_2M_BARS
signal_2_candidate: RSI_14_OF_COPPER_GOLD_ON_2M_BARS
primary_anchor_candidate: YEAR_ANCHORED_JAN_FEB
color_convention_claim:
  histogram_above_zero: RED
  histogram_below_or_equal_zero: GREEN
source_claim: TECHDEV_ISSUES_62_65_67_69_75_85_86_94
series_status: RECONSTRUCTION_NOT_VENDOR_SERIES
```

This strongly upgrades the exact-algorithm hypothesis. However, the ZIP does not contain the cited TechDev issue excerpts or vendor series. Exact canonical ratification therefore still requires either the primary archived excerpts with source lineage or an independently reviewable source object.

The current Jan-Feb 2026 Jul-Aug bar is in progress. It must not be treated as a settled flip before the bar end.

## 5. Critical test-implementation audit

No supplied script was executed during this audit. Static review of the packaged code and outputs found multiple load-bearing mismatches between declared tests and implemented calculations.

### A. BT08 business-cycle lookahead

The reconstruction indexes every 2M bar at its **start date**. The event study then measures forward returns from that start date, and the daily master/state panels forward-fill the final bar value from the start date.

Therefore the supplied BT08 returns, drawdowns and daily phase medians use information that was not knowable until the 2M bar settled. The package itself logs this warning, but the upstream BT08 output was still calculated with the contaminated timestamps.

```yaml
BT08_upstream_results: QUARANTINED_NOT_SCOREABLE
required_repair: SHIFT_SIGNAL_KNOWLEDGE_TIME_TO_SETTLED_BAR_END
current_2026_07_bar: EXCLUDE_UNTIL_SETTLED
```

### B. BT01 ETF session weighting and knowledge-time mismatch

The code reindexes session-level ETF features onto a daily calendar, forward-fills them, and then applies a one-calendar-day shift. This repeats the same flow observation across non-session days and produces samples larger than the available ETF sessions:

```yaml
BTC_ETF_sessions: 651
upstream_BT01_BTC_n: up_to_925
ETH_ETF_sessions: 513
upstream_BT01_ETH_n: up_to_731
```

The implementation is not a one-row-per-completed-session test and does not enforce the advertised session-based knowledge-time contract.

### C. BT09 target mismatch

The code labelled `WEEKEND_TO_MONDAY_ETF` calculates percentage change between consecutive Sunday observations. It does not calculate weekend movement against the next completed US ETF session and does not use ETF outcomes.

```yaml
BT09_upstream_result: INVALID_FOR_DECLARED_HYPOTHESIS
```

### D. BT03 condition mismatch

The implemented BT03 trigger is only `consec_pos >= 3`. It omits the declared ETH leadership and breadth or dominance confirmation requirements. It is not the H7-style early-transmission test described in the readiness matrix.

### E. BT06 incomplete implementation

The code groups by funding z-score only. Open-interest state is not included despite the declared `FUNDING_OI_CONFIRMATION` hypothesis.

### F. BT07 incomplete implementation

The code reports unconditional ETH/BTC returns by breadth tercile. It does not condition the performance of an ETH/BTC transmission signal on breadth.

### G. BT02 absent implementation

BT02 is declared `READY`, but no BT02 result is produced by the supplied preliminary-test script.

### H. BT05 framework-rule mismatch

The implementation compares fixed calendar delays after a one-day BTC loss below -8%. It does not implement the framework's confirmation gates, state locks, event deduplication or overlapping-event controls. It is a useful prototype only.

### I. BT10 missing decision ledger

No forecast, decision, threshold-change or framework-state ledger is present in the package. A point-in-time framework replay cannot be implemented from the master market panel alone.

## 6. Readiness correction

The package's own `READY` and `READY_WITH_RESTRICTIONS` labels are non-governing and are not accepted as test authorization.

A more accurate separation is:

```yaml
data_collection_readiness: HIGH
feature_research_value: HIGH
owner_dataset_selection: PENDING
point_in_time_contracts: PARTIAL
backtest_code_readiness: FAIL_REPAIR_REQUIRED
preliminary_results_authority: NONE
controlled_test_execution: LOCKED
```

Direct price, ETF, breadth and derivatives data may become owner candidates after deduplication and source-method review. The current test implementations require rewrite and regression fixtures before controlled execution.

## 7. Decision

```yaml
package_identity: ACCEPTED
payload_integrity: PASS_WITH_CHECKSUM_SCOPE_NOTE
raw_data_archive_value: HIGH
canonical_backtest_dataset: NOT_YET
techdev_exact_spec: HIGH_CONFIDENCE_CANDIDATE_NOT_RATIFIED
BT08_results: QUARANTINED_LOOKAHEAD_CONTAMINATED
other_preliminary_test_results: QUARANTINED_IMPLEMENTATION_MISMATCHES
test_execution: LOCKED
historical_edge_claim: NONE
market_interpretation: NONE
framework_state_change: NONE
portfolio_action: NONE
next_gate: DEDUPLICATE_SELECT_OWNER_DATASETS_AND_REWRITE_TEST_CONTRACTS
```

The raw archive is a major contribution to BACKTEST BUILD. Its supplied performance tables do not yet constitute valid framework backtests.