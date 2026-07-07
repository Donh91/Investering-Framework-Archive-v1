# Custom GPT Sensor Supplement — Research Operating System v1.1

Date received: 2026-07-07  
Source role: DATA PING sensor / archive extraction only  
Governance status: NON-BINDING DATA SUPPLEMENT  
Use: update Evidence Registry, Open Questions Register, Data Asset Manifest and Replay Harness readiness.

---

## 0. Role boundary

This supplement is data input only.

It does not:

- make market calls
- authorize portfolio action
- ratify rules
- unlock rebuy
- confirm recovery
- confirm rotation
- create official rows

Custom GPT remains sensor/archive extraction layer only.

---

## 1. Active DATA PING version

| Version/layer | Status | Role | Confidence | Notes |
|---|---|---|---|---|
| DATA_PING_V4 | ACTIVE | LIVE_SENSOR_OUTPUT | 0.86 | Highest active live output observed. |
| DATA_PING_GOVERNANCE_SPEC_v2_6_FREE_ONLY | ACTIVE_BASE_SPEC | GOVERNANCE_BASE | 0.95 | Required printed spec version. |
| DATA_PING_V4_1_RAW_FORECAST_IMPROVEMENT_PATCH_v1 | ACTIVE_PATCH | DATA_FIELDS_PATCH | 0.82 | Adds close ledger, ETF verification, breadth persistence, stablecoin official, range, derivatives, BTC.D consistency and raw input support summary. |
| DATA_PING_V4_2_FALLBACK_LABELS | ACTIVE_LABEL_PATCH | FALLBACK_LABELS | 0.70 | Fallback concepts/labels active in output; not a full separate archive file found. |
| DATA_PING_CFGI_SENTIMENT_LAYER_v1_FREE_PUBLIC | ACTIVE_LAYER | SENTIMENT_DATA_ONLY | 0.74 | CFGI public sentiment input; historical rows missing without API. |
| DATA_PING_FRED_CLASSIC_V1_2_MACRO_LAYER | ACTIVE_MACRO_LAYER | MACRO_SHADOW | 0.92 | FRED Classic v1.2 is targeted-series production macro feed; macro remains shadow only. |
| OLDER_DATA_PING_VERSIONS | ARCHIVE_CONTEXT_ONLY | HISTORICAL_CONTEXT | 0.80 | Older rows usable only as historical/as-of context when active at historical timestamp. |

Governance interpretation:

- DATA_PING_V4 remains active live sensor layer.
- DATA_PING spec version and patches should be added to source-governance tracking.
- FRED and CFGI remain shadow/data-only layers.

---

## 2. Schema highlights

The supplement confirms the current DATA PING schema includes:

- timestamp / snapshot ID / spec version
- source status and freshness
- BTC / ETH / ETHBTC / BTC.D
- close ledger and BTC rung input
- breadth input and breadth persistence
- ETF flow verification
- CVD / spotflow if explicit source exists
- stablecoin official and chain distribution distinction
- TVL input
- funding/OI derivatives
- range input
- BTC.D consistency check
- CFGI sentiment
- FRED macro shadow
- source conflicts
- gate/FNP/path inputs only
- framework interpretation boundary

Important schema rule:

`DATA PING supplies inputs only; framework interpretation is deferred to governance.`

---

## 3. Recent DATA PING rows extracted

### 2026-07-07T06:31Z

- BTC: 63168.74
- ETH: 1770.96
- ETHBTC: 0.028030
- BTC.D: 55.8105
- BTC ETF latest: 06 Jul +265.7M
- BTC ETF trend: IMPROVING / NOT_FULLY_CONFIRMED
- BTC ETF streak: 2
- ETH ETF latest: 06 Jul +20.7M
- Funding/OI: BTC funding +0.007998%, BTC OI ~6.39B USD; ETH funding -0.000381%, ETH OI ~4.00B USD
- Breadth: 1H 31/35=89%, 24H 15/35=43%, 7D 31/35=89%
- State: NOT_DETERMINED_BY_DATA_PING
- Rebuy: NOT_DETERMINED_BY_DATA_PING
- Gate: v0.2 row NOT DETERMINED BY DATA PING
- FNP: deferred / NOT_DETERMINED_BY_DATA_PING
- Data quality: MEDIUM
- Source conflicts: BTC/ETH/ETHBTC OK; BTC.D NOT_COMPUTABLE single-source

### 2026-07-07T00:01Z

- BTC: 64043.77
- ETH: 1799.31
- ETHBTC: 0.028100
- BTC.D: 55.9349
- BTC ETF latest: 02 Jul +223.5M; 06 Jul partial +46.6M not final
- BTC ETF trend: IMPROVING / NOT_CONFIRMED
- ETH ETF latest: 02 Jul +29.0M; 06 Jul pending
- Breadth: 1H 5/35=14%, 24H 11/35=31%, 7D 30/35=86%
- Data quality: MEDIUM
- Note: 06 Jul ETF not final in this row

### 2026-07-06T21:26Z

- BTC: 64236.75
- ETH: 1815.53
- ETHBTC: 0.028270
- BTC.D: 55.88
- BTC ETF latest: 02 Jul +223.5M
- BTC ETF trend: IMPROVING / NOT_CONFIRMED
- ETH ETF latest: 02 Jul +29.0M
- Breadth: 1H 34/35=97%, 24H 20/35=57%, 7D 31/35=89%
- Data quality: MEDIUM
- Note: latest completed close at that time was 2026-07-05 CEST; current candle was partial

Governance interpretation:

- These rows are useful for replay-row seed data.
- They do not create official framework state.
- ETF 06 Jul placeholder vs finalized row must be reconciled before replay scoring.

---

## 4. Master Monday archive status

Status: MISSING

No accessible Master Monday forecast rows/files were found by Custom GPT.

Governance consequence:

- Weekly Master Monday replay is not ready.
- Need file paths or uploaded Master Monday archive.

---

## 5. Cycle Navigator archive status

Status: MISSING

No accessible Cycle Navigator weekly post manifest was found by Custom GPT.

Governance consequence:

- Cycle Navigator Range Skill Audit is not ready from Custom GPT alone.
- Need file paths or uploaded/exported Cycle Navigator archive.

---

## 6. Verified weekly actuals

Available partial actual:

| Week | Date span | BTC high | BTC low | ETH high | ETH low | Source | Run ID | Status |
|---|---|---:|---:|---:|---:|---|---|---|
| 2026-W27 | 2026-06-29 to 2026-07-05 | 63461.99 | 57800.19 | 1807.65 | 1548.37 | Binance CEST daily klines / W27 final price close pack | FRED_MARKET_WEEKLY_BACKTEST_W27_20260706 | FINAL_PRICE_CLOSE |

Notes:

- BTC open 59445.96, close 63092.01
- ETH open 1563.63, close 1786.88
- ETHBTC end 0.02832
- BTC_TOUCH_63.3K YES
- BTC_CLOSE>63.3K NO
- BTC_CLOSE>61.9K YES

Governance consequence:

- W27 actual can be used in weekly actuals ledger, but earlier user-verified W27 values may need reconciliation against this Binance CEST pack.
- Source differences must be retained, not overwritten silently.

---

## 7. ETF archive path status

| Asset | Source/path | Date span | Status | Notes |
|---|---|---|---|---|
| BTC | Farside public web bitcoin-etf-flow-all-data | 2024-01-11 to current | AVAILABLE_PUBLIC_WEB | Latest live row 06 Jul +265.7M. |
| ETH | Farside public web eth | 2024-07-23 to current | AVAILABLE_PUBLIC_WEB | Latest live row 06 Jul +20.7M. |
| BTC archive dump | file-library ETF dump | 2024-01-11 to 2026-07-06 | PARTIAL_ARCHIVE_DUMP | Contains placeholder rows requiring reconciliation. |
| ETH archive dump | file-library ETF dump | 2024-07-23 to 2026-07-06 | PARTIAL_ARCHIVE_DUMP | Contains placeholder rows requiring reconciliation. |
| SoSoValue/CoinDesk | manual/cross-check | 2026-07-02 partial | PARTIAL_MANUAL_CONTEXT | Cross-check only, no full archive. |
| GitHub ETF archive path | `08_SOURCE_MATERIAL/market_data/etf_flows/` | unknown | PATH_KNOWN_CONTENT_NOT_VERIFIED | Needs GitHub verification. |

Governance consequence:

- ETF studies are partial-ready.
- 06 Jul placeholder vs finalized Farside rows must be reconciled before scoring.
- Farside is public table, not official API.

---

## 8. Data quality summary

| Section | Status | Confidence | Main issue | Next action |
|---|---|---:|---|---|
| Active DATA PING version | AVAILABLE | 0.86 | Inferred from current live output; no canonical manifest file | Export canonical version manifest |
| DATA PING schema | PARTIAL | 0.78 | Reconstructed from rows/patch context | Export schema CSV/JSON |
| Recent DATA PING rows | AVAILABLE | 0.90 | Latest rows only | Archive with snapshot IDs |
| Master Monday archive | MISSING | 0.15 | No forecast files found | Provide/upload archive |
| Cycle Navigator archive | MISSING | 0.15 | No manifest found | Provide/upload archive |
| Verified weekly actuals | PARTIAL | 0.75 | W27 only | Attach full weekly actuals extractor output |
| ETF archive paths | PARTIAL | 0.82 | Placeholder/final mismatch | Lock source cutoff and reconcile |
| Price/range extractor | AVAILABLE | 0.90 | README available; CSV not attached | Run extractor and attach output |
| FRED macro | AVAILABLE | 0.92 | Shadow only | Keep separated from live state |
| CFGI sentiment | PARTIAL | 0.70 | History missing | Add explicit export if needed |
| Stablecoin official | PARTIAL | 0.45 | Official mcap/7D/30D failed in latest rows | Restore DeFiLlama overview/chart extraction |
| Breadth ledger | PARTIAL | 0.55 | Full daily replay ledger missing | Export fixed universe daily rows |
| Derivatives ledger | PARTIAL | 0.60 | Full replay-window ledger missing | Export funding/OI/L/S/taker rows |

---

## 9. Replay readiness update

| Replay/test | Readiness | Available | Missing | Next action |
|---|---|---|---|---|
| P1b gate window replay 2026-06-02 to 2026-07-02 | PARTIAL_READY_WITH_MISSING_DATA | Price/range design, Binance CEST OHLC fields, ETF archive/dumps, FRED shadow | Daily DATA PING rows, breadth ledger, BTC.D ledger, stablecoin official, funding/OI full window | Run extractor and export daily ledgers |
| Weekly Cycle Navigator range skill audit | NOT_READY | W27 actuals | Forecast issue manifest, ranges, dates, scores | Upload/paste Cycle Navigator archive |
| ETH/BTC persistence test | READY_PRICE_ONLY | ETHBTC direct/CEST close fields; W27 actual | Full historical ETHBTC CSV not attached | Run price/range extractor |
| ETF stabilization formula study | PARTIAL_READY_WITH_CAUTION | BTC/ETH Farside sources, latest rows | As-of finalized timestamp, 06 Jul reconciliation | Lock completed-trading-day rule |
| Gradueret deployment backtest | NOT_READY | Price/ETF partial | Breadth/BTC.D/stablecoin/alt proxy/fake rotation ledgers | Build fixed daily ledgers |
| Gate-BTC partial shadow test | PARTIAL_READY | BTC/ETH/ETHBTC price/range and W27 actual | Forward-test ledger rows | Create no-hindsight forward-test rows |

---

## 10. Governance intake requirements

Custom GPT requested the following governance actions:

1. Export canonical active DATA PING version manifest.
2. Provide Master Monday forecast files/paths.
3. Provide Cycle Navigator weekly post files/paths.
4. Reconcile 06 Jul ETF placeholder dumps vs finalized Farside rows.
5. Lock daily replay source-cutoff rules.
6. Generate fixed daily ledgers for breadth, BTC.D, stablecoin official, funding/OI and ETF flows.
7. Keep DATA PING as sensor/archive layer only.

Governance response:

- Accepted as intake requirements.
- No rule ratification occurs from this supplement alone.
- Most urgent operational improvement is canonical version manifest + ETF final/placeholder reconciliation + replay source-cutoff rules.
