# Data Asset Manifest v1.0

Date: 2026-07-07  
Status: INITIAL DATA ASSET MAP  
Purpose: Map which data assets exist, which are missing, and what each asset can be used for.

---

## Asset status legend

| Status | Meaning |
|---|---|
| AVAILABLE | Asset exists or has been successfully ingested. |
| PARTIAL | Asset exists but is incomplete or limited. |
| SOURCE-MAPPED | Source is known but not yet ingested/tested. |
| MISSING | Required asset not currently available. |
| ARCHIVE-CONTEXT | Useful for context, not a clean dataset yet. |
| NEEDS-EXTRACTION | Exists in text/PDF/archive but must be structured. |

---

## Current assets

| Asset | Status | Location / source | Use | Limitation |
|---|---|---|---|---|
| Fable P1 close-only results | AVAILABLE | `05_RESEARCH_LAB/fable_research/p1_executed/` and uploaded P1 files | E3/E5/E8 baseline evidence | Close-only / price-only |
| Fable P1b executed results | AVAILABLE | `05_RESEARCH_LAB/fable_research/p1b_ohlc_flow_upgrade/` | OHLC + flow-conditioned governance evidence | FMP composite, small cells |
| P1b FMP OHLC master | AVAILABLE in uploaded artifact | `btc ohlc master.csv` from Fable thread | True OHLC / ATR / E5-OHLC | Not Binance primary |
| P1b Farside BTC ETF flow | AVAILABLE in uploaded artifact | `etf flow daily.csv` from Fable thread | ETF-era flow conditioning | Starts 2024-01-11; BTC ETF only |
| Fable recommendation rows | AVAILABLE | GitHub archived markdown | Governance implementation rows | Non-binding without ChatGPT ratification |
| DATA PING V4 live context | ARCHIVE-CONTEXT | Project memory / archive | Live operational truth feed | Needs structured extraction |
| DATA PING V1-V3 | ARCHIVE-CONTEXT | Uploaded/archive files | Historical context and training rows | Older versions are archive-only unless highest active at time |
| Master Monday raw files | NEEDS-EXTRACTION | GitHub/archive, if present | Weekly replay and public-report history | Need file manifest and structured fields |
| Cycle Navigator weekly posts | NEEDS-EXTRACTION | Archive / user-provided history | Forecast skill and score audit | Need canonical forecast/actual rows |
| Verified weekly actual ranges | PARTIAL | Project memories + uploaded range data | Range-model evaluation | Need complete weekly table |
| BTC ETF flows historical | PARTIAL/AVAILABLE | Farside via Fable P1b; GitHub ETF archive likely exists | ETF stabilization / flow regimes | Need canonical path and merged daily file |
| ETH ETF flows historical | SOURCE-MAPPED | Farside / user ETF archive | ETH/BTC and rotation context | Need ingestion |
| ETH/BTC daily | MISSING/SOURCE-MAPPED | Binance/CoinGecko/FMP possible | E2 ETH/BTC persistence | Need direct pair or same-source derived |
| Breadth history | MISSING | TBD | Rotation confirmation / E3 breadth-conditioned | No reliable free historical source selected |
| BTC.D history | PARTIAL/SOURCE-MAPPED | CoinGecko / other | Rotation regime | Needs verified daily series |
| Funding/OI history | MISSING | Binance futures or other | Leverage reset / squeeze vs repair | Historical access unresolved |
| Liquidation clusters | MISSING | Coinglass/other | Stress/flush add-on | Likely paid/API |
| Stablecoin supply | SOURCE-MAPPED | DeFiLlama stablecoins | Liquidity regime / E12 | Needs ingestion and daily alignment |
| DeFi TVL | SOURCE-MAPPED | DeFiLlama TVL | Liquidity regime / E12 | Needs ingestion and daily alignment |
| Macro/FRED | SOURCE-MAPPED | FRED | Macro context | Lower priority |
| Options/Deribit | SOURCE-MAPPED | Deribit API | IV/skew/gamma context | Not P1/P1b priority |
| Sentiment Alternative.me | SOURCE-MAPPED | Alternative.me API | Sentiment layer | Not validated for decisions |

---

## Canonical source priority by test

### E5-OHLC / gate testing

Preferred:

1. Binance Spot OHLC, if accessible
2. FMP eod-full OHLC as sanctioned fallback
3. CoinGecko OHLC as fallback if sanity gates pass

Required fields:

- date
- open
- high
- low
- close
- ATR14

### E3-FULL / close-persistence conditioning

Required fields:

- BTC OHLC
- ETF daily net flow
- ETF trailing flow trend
- optional breadth proxy
- optional funding/OI

### E8-FULL / FNP cost conditioning

Required fields:

- BTC OHLC
- pullback episodes
- first permitted entries
- ETF flow from low to entry
- forward returns

### E2 / ETHBTC persistence

Required fields:

- ETHBTC direct pair daily close, preferred
- same-source ETH close / BTC close, fallback
- forward returns in ETH, BTC and ETHBTC
- rotation proxy if possible

### Cycle Navigator range skill audit

Required fields:

- forecast week number
- forecast date
- BTC forecast low/high
- ETH forecast low/high
- actual BTC low/high
- actual ETH low/high
- forecast width
- actual containment
- breach direction
- regime label
- score displayed
- dumb baseline comparison

---

## Data quality rules

1. Every dataset must include source, date span, gaps and sanity checks.
2. If source changes, mark SOURCE_SWITCH.
3. Derived ETH/BTC must be marked derived.
4. FMP composite data must not be labeled exchange-primary.
5. Farside scrape/reference must be logged as scrape/reference, not official API.
6. Missing data must be marked DATA_MISSING, not assumed neutral.
7. ETF latest pending must carry latest known context, not blank status.
8. Perp wicks remain diagnostic-only unless a dedicated spot/perp study ratifies otherwise.

---

## Most valuable missing data now

1. ETHBTC daily series.
2. Canonical Cycle Navigator weekly forecast/actual table.
3. Canonical Master Monday raw archive list.
4. Historical funding/OI source.
5. Historical breadth proxy.

---

## Immediate use

This manifest supports the No-Hindsight Replay Harness by defining which data can be trusted today and which fields must be marked missing during replay.
