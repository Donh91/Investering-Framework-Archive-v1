# Claude Week 29 Research Package - Source and QA Note

**Dato:** 2026-07-19  
**Status:** SOURCE_NOTE / PARTIAL_PASS_WITH_BLOCKING_LIMITATIONS  
**Område:** Claude Research Lab / W29 source package / forecast audit input  
**Primary folder:** `08_SOURCE_MATERIAL/claude/`  
**Related folders:** `06_RESEARCH_LAB/audit_summaries/`, `03_WEEKLY_OPERATIONS/forecast_ledger/`, `02_DATA_PING/decision_value/`  
**Depends on:** `03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-13__forecast-ledger-2026-w29__official.md`, `01_CORE_FRAMEWORK/governance/2026-07-10__f12-f12-5-reproducibility-freeze__canonical.md`, `04_MARKET_LEARNING/shadow_protocols/2026-07-12__transmission-matrix-forward-falsification-protocol-v0-1__canonical.md`

---

## 1. Source package

```text
Uploaded ZIP: CLAUDE WEEK29 RESEARCH PACKAGE 2026.zip
Claimed package name: CLAUDE_WEEK29_RESEARCH_PACKAGE_2026.zip
ZIP SHA-256: dc9e2362dbe03500fcef560810f4ac3303179b861934524a64a62af47cc8a889
ZIP hash verification: PASS
Files present: 14
Requested files present: 14/14
Binary ZIP stored in GitHub: NO
```

Companion PDFs received:

```text
00 EXECUTIVE VERDICT.pdf
SHA-256: f0b9e0daa2ce1b755f8dace74da641fc6cbd7ca964175365a9a5de37fde267a8

09 FRAMEWORK RED TEAM.pdf
SHA-256: 03566aa4deaef494660a5f89bf1c04be4a827a8a8908f7ba9e82de0b99e79c80
```

Package members:

```text
00_EXECUTIVE_VERDICT.md
01_WEEK29_VERIFIED_ACTUALS.csv
02_WEEK29_CHRONOLOGY.csv
03_ETF_SESSION_LEDGER.csv
04_MULTI_VENUE_FLOW_PANEL.csv
05_MACRO_RELEASE_LEDGER.csv
06_CLAIM_EVIDENCE_LEDGER.csv
07_SOURCE_AND_CONFLICT_LEDGER.csv
08_WEEK29_FORECAST_AUDIT.md
09_FRAMEWORK_RED_TEAM.md
10_DATA_GAP_PRIORITY.md
11_ARCHIVE_RECOMMENDATIONS.md
12_FULL_RESEARCH_REPORT.md
13_MACHINE_READABLE_SUMMARY.json
```

## 2. Technical package result

```text
ZIP_READABLE: PASS
FILE_COUNT: PASS_14_OF_14
MACHINE_READABLE_JSON: PASS_PARSEABLE
CSV_PARSEABILITY: PASS
INTERNAL_CHECKSUM_MANIFEST: ABSENT
RAW_API_RESPONSES: ABSENT
REQUEST_LEDGER: ABSENT
REPRODUCTION_SCRIPT: ABSENT
SOURCE_RECEIPTS_WITH_RETRIEVAL_TIMESTAMPS: INCOMPLETE
FULL_NUMERIC_REPRODUCIBILITY: FAIL
```

The package is structurally useful as a Research Lab synthesis. It is not a reproducible truth-layer archive because it contains no raw API responses, request ledger, extraction script or package-member checksum manifest.

## 3. Blocking limitations for official W29 actuals or scoring

### A. Wrong price convention for the official ledger

The frozen W29 Forecast Ledger requires:

```text
BINANCE_SPOT_USDT
CEST_RESAMPLED
complete settled week
provider mixing forbidden
```

The Claude package instead uses:

```text
Crypto.com 1D UTC
```

This is a legitimate independent source convention, but it is not the frozen evaluation convention. Therefore its high, low, close and range values may not be written into the official W29 score chain.

Classification:

```text
INDEPENDENT_SHADOW_PRICE_AUDIT: ALLOWED
OFFICIAL_W29_VERIFIED_ACTUAL: NOT_ELIGIBLE
OFFICIAL_SCORE_ROW: FORBIDDEN
```

### B. Week was not settled

The package includes 19 July as `PARTIAL` and uses 18 July as the last settled close while repeatedly describing the W29 range or outcome as settled.

At package creation:

```text
SUNDAY_CANDLE: PARTIAL
W29_WEEKLY_CLOSE: NOT_SETTLED
FINAL_FORECAST_OUTCOME: NOT_MATURE
```

The intrawweek range may be logged as provisional. It may not be treated as the complete-week final outcome until the Sunday CEST candle settles.

### C. ETF ledger is not a complete 20-session ledger

The 20-row file contains:

```text
16 settled rows
1 provisional row
1 pending row
2 weekend rows
```

It is therefore not 20 completed sessions. Several completed trading sessions and multiple IBIT/ETH fields are absent.

The package's 3/5/7/10-session sums were calculated over the available numeric rows rather than a complete contiguous primary-source session sequence.

Classification:

```text
ETF_SESSION_LEDGER_COMPLETENESS: FAIL
CLAIMED_20_COMPLETED_SESSIONS: FALSE
WINDOW_AGGREGATES_AS_ARCHIVE_TRUTH: REJECT
```

### D. 17 July ETF values were provisional and are now stale

The package uses Lookonchain estimates:

```text
BTC 17 Jul: +83.2M
ETH 17 Jul: +4.3M
```

Farside primary subsequently completed the session as:

```text
BTC 17 Jul: +132.3M
IBIT 17 Jul: +136.5M
ETH 17 Jul: +36.7M
```

Consequences:

```text
4-session streak existence: CONFIRMED
4th-session magnitude: PACKAGE_VALUE_STALE
claimed deceleration 181.1 -> 107.7 -> 79.1 -> 83.2: INVALID
package ETF rolling windows: INVALID
package 10-session -263.2M conclusion: NOT_ARCHIVEABLE
```

### E. Multi-venue task was not completed

`04_MULTI_VENUE_FLOW_PANEL.csv` contains five rows, mostly unavailable or gap labels. It does not provide multi-venue confirmation and correctly does not construct market-wide CVD.

```text
MARKET_WIDE_CVD: METHOD_GAP / UNAVAILABLE
MULTI_VENUE_SPOT_CONFIRMATION: NOT_PRODUCED
```

### F. Macro sourcing is incomplete

The CPI values are directionally consistent with the official BLS release, but the package records them as `BLS via Tier2` and does not preserve the official release response, retrieval timestamp or expectation-source lineage.

The Japan entry is also overstated as a specific `spot crypto ETF 20% tax framework approved`. The durable source-backed development was a legal reclassification of crypto assets as financial assets. The package's narrower ETF/tax formulation is not retained as archive fact.

## 4. Source claims that passed or remain useful

The following are retained only in shadow or source-note roles:

```text
1. W29 exhibited a strong intrawweek BTC repair sequence.
2. BTC 63.3K reclaim and 61.9K survival remained decision-relevant event observations.
3. ETH/BTC remained above the 0.0275 repair threshold and below 0.0300 confirmation in the package window.
4. 16 July primary Farside flows were BTC +79.1M and ETH -28.0M.
5. The BTC/ETH ETF flow-leg divergence is relevant to transmission quality.
6. Market-wide CVD remains unavailable and must not be inferred.
7. The package's red-team focus on falsifiability is methodologically valid.
```

These facts do not independently establish broad recovery, rotation, entry permission or portfolio action.

## 5. Duplicate and overlap ruling

The following package conclusions were already present in canonical or operational context before ingestion:

```text
NO_ROTATION
LARGE_CAP_WINDOW_LOCKED
ETHBTC_REPAIR_ABOVE_0275_BUT_BELOW_0300
BTC_ETF_STAGE1_FLOW_LEG_COMPLETE
ETH_ETF_16JUL_MINUS_28M
FIXED_RISK35_CANONICAL_UNAVAILABLE
MARKET_WIDE_CVD_UNAVAILABLE
STABLECOIN_TVL_DEX_CURRENT_DELTA_INCOMPLETE
```

They are not archived as new standalone rows.

## 6. Final source disposition

```text
PACKAGE_ARCHIVE_DECISION: PARTIAL_ACCEPT
SOURCE_PROVENANCE_NOTE: ARCHIVE
RED_TEAM_SYNTHESIS: ARCHIVE_AS_SHADOW
RAW_DATASET_PROMOTION: REJECT
OFFICIAL_W29_ACTUAL: REJECT_PENDING_SETTLEMENT_AND_CORRECT_CONVENTION
OFFICIAL_FORECAST_SCORE: REJECT
NEW_CANONICAL_RULE: REJECT
NEW_FORWARD_TEST: REJECT_UNDER_ACTIVE_TEST_FREEZE
PORTFOLIO_AUTHORITY: ZERO
```

The durable value is the QA trail and the falsifiability-focused red-team synthesis, not the package's provisional numeric outcome claims.
