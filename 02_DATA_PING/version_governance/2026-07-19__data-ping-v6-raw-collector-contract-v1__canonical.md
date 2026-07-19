# DATA PING V6 Raw Collector Contract v1.0

**Dato:** 2026-07-19 16:43 CEST  
**Status:** CANONICAL_OPERATIONAL  
**Område:** DATA PING V6 / raw collector / AI-to-AI ingest  
**Primary folder:** `02_DATA_PING/version_governance/`  
**Depends on:** `02_DATA_PING/protocols/2026-07-15__data-ping-thread-handover-protocol-v1-0__canonical.md`, `02_DATA_PING/operational_handoffs/latest_accepted_log_state.json`, `02_DATA_PING/operational_handoffs/latest_decision_context_state.json`  
**Activation:** first complete V6 packet reviewed and accepted by ChatGPT/Main Framework  
**Supersedes for V6:** `DATA_PING_MAIN_THREAD_INGEST_v1_1` collector layout; V5 history remains immutable

## 1. Purpose

V6 separates source collection from framework computation.

```text
Custom GPT / DATA PING collector
= verified source observations, source ledgers and reproducible source aggregates

ChatGPT / Main Framework
= CLV, range position, retention, gates, falsifiers, Stage-1, recovery, rotation, permissions, action and canonical acceptance
```

The collector must not own framework interpretation or duplicate framework calculations.

## 2. Exact wire format

A normal V6 response must contain exactly:

```text
DATA_PING_MAIN_THREAD_INGEST_BEGIN
{one valid JSON object with exactly 11 top-level fields}
DATA_PING_MAIN_THREAD_INGEST_END
IGNORE FOR MAIN-FRAMEWORK INGEST
PACKET_SHA256: <optional hash or NOT_GENERATED>
```

No progress commentary, Markdown tables, human summary, download list, ZIP, sidecar files or repeated prose/JSON data unless explicitly requested.

## 3. Frozen 11-field schema

The top-level fields are exactly:

```text
1. packet
2. meta
3. quality
4. source_health
5. observations
6. source_ledgers
7. deterministic_source_aggregates
8. readiness
9. missing
10. artifacts
11. authority
```

Packet contract:

```text
DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
```

The V5 fields `deterministic_derived`, `experimental_shadow` and `collector_interpretation_nonbinding` are not part of the standard V6 packet.

## 4. Identity and lineage

Every packet must include under `meta`:

```text
snapshot_id
snapshot_utc
snapshot_cest
execution_mode
snapshot_status
canonical_predecessor_id
collector_predecessor_id
method_versions
source_receipts
packet_hash_status
```

Rules:

- `canonical_predecessor_id` points to the latest Main-Framework accepted DATA PING.
- `collector_predecessor_id` may point to the latest method-compatible raw collector packet.
- A validation-only V5 packet never becomes canonical merely because it is the collector predecessor.
- Every timestamp must identify UTC/CEST convention and settled/partial status.

## 5. Source ledgers required on full runs

### A. Weekly spot structure

Persist the complete current ISO-week source rows for:

- BTC CEST daily OHLCV;
- ETH CEST daily OHLCV;
- direct ETH/BTC CEST daily OHLC;
- latest settled candle;
- current partial candle;
- exact source timestamps and timezone convention.

Rolling 24H data must never substitute for a CEST daily candle.

The collector may report a source-native weekly OHLC convenience aggregate, but the daily rows remain authoritative and Main Framework recomputes weekly values, CLV, range position, retention and threshold observations.

### B. ETF and IBIT session ledger

Persist at least the latest ten completed sessions individually:

```text
session_date
btc_total_usd_m
ibit_usd_m
eth_total_usd_m
primary_source
source_timestamp_or_verification_timestamp
revision_status
```

Rules:

- Farside is primary.
- Lookonchain, OTA or other sources are separate provisional observations.
- Primary and secondary values are never averaged or silently overwritten.
- Weekend is `NO_SESSION_WEEKEND`, never flow `0`.
- 3/5/7/10-session totals may be supplied only when the underlying session rows are present.

### C. Binance Spot taker inputs

Method is frozen to:

```text
DIRECT_SETTLED_HORIZONS_v1
```

For BTC and ETH, return 15M, 1H, 4H and 24H with:

```text
window_start
window_end
total_quote_volume
taker_buy_quote_volume
net_taker_quote
buy_share
window_status: SETTLED | PARTIAL
method_version
```

No predecessor delta may be reported unless method version and window definition match exactly.

### D. Futures and leverage

Return source-native inputs for BTC and ETH:

- funding;
- mark and index price;
- basis;
- open interest and notional convention;
- OI history required for 1H/4H/24H deltas;
- futures taker ratios;
- venue-specific long/short observations.

All exchange observations must remain labelled `NOT_MARKET_WIDE`.

### E. Reproducible dynamic breadth

Persist:

- exact CoinGecko IDs and symbols included;
- excluded IDs and exclusion reasons;
- membership hash;
- source timestamp range;
- raw 1H/24H/7D rows or sufficient source rows for recomputation;
- sample count;
- ex-BTC and ex-BTC+ETH membership.

If membership hash changes:

```text
BREADTH_DELTA_STATUS: NOT_COMPARABLE_SAMPLE_CHANGED
```

Dynamic breadth remains `SHADOW_ONLY` and does not replace canonical fixed breadth.

### F. FIXED_RISK35

`FIXED_RISK35_v1` may be computed only when the original authoritative membership, provenance and hash are available.

Otherwise:

```text
FIXED_RISK35_STATUS: UNKNOWN
RECONSTRUCTION_FORBIDDEN: true
```

A candidate 35-ID set may be labelled only:

```text
CANDIDATE_SHADOW
NOT_CANONICAL
NOT_PROMOTED
```

Missing canonical FIXED_RISK35 must not block a full DATA PING, Sunday closeout or Master Monday raw-input package.

### G. Other source observations

Return available source-native observations for:

- official stablecoin total/history;
- separately labelled USDT+USDC proxy;
- current TVL and timestamp status;
- DEX proxy rows and timestamp status;
- CFGI with page/source timestamps;
- date-native macro observations.

Market-wide CVD remains unavailable unless a genuine approved source exists.

## 6. Allowed deterministic source aggregates

Collector-side aggregates are convenience values only and must be reproducible from included source rows.

Allowed examples:

- ETF 3/5/7/10-session sums;
- weekly OHLC convenience aggregate from included daily rows;
- breadth average, median, quartiles and advancing counts from included membership rows;
- `net_taker_quote = 2 * taker_buy_quote_volume - total_quote_volume`;
- buy share from supplied quote-volume constituents.

Not collector-owned:

- CLV;
- range position;
- retention;
- BTC rung or gate results;
- ETH/BTC threshold results;
- follow-through quality;
- recovery-attempt quality;
- divergence interpretation;
- market-input-up/down classification;
- Stage-1;
- FNP;
- recovery, rotation, rebuy, deployment or portfolio action.

These remain Main-Framework computations.

## 7. Readiness block

`readiness` reports raw-data availability only, using exactly:

```text
YES
NO
UNKNOWN
NOT_DUE
```

Required fields:

```text
sunday_settled_weekly_candle_available
btc_weekly_ohlcv_available
eth_weekly_ohlcv_available
ethbtc_weekly_ohlc_available
farside_btc_session_ledger_available
farside_eth_session_ledger_available
ibit_session_ledger_available
p1_reference_observation_available
fixed_risk35_canonical_available
official_stablecoin_history_available
market_wide_cvd_available
outstanding_raw_inputs
```

Readiness must not report whether Stage-1, thresholds, recovery or rotation passes.

## 8. Missing-data semantics

Use distinct statuses:

```text
MISSING
UNKNOWN
UNAVAILABLE
NOT_DUE
NOT_COMPARABLE
DEFERRED_TO_MAIN_FRAMEWORK
NO_SESSION_WEEKEND
```

Numeric missing fields use:

```json
{"value": null, "status": "UNKNOWN"}
```

Never use a string such as `"UNKNOWN"` as a numeric value. No reconstruction or interpolation.

## 9. Artifact default

Standard output:

```json
{
  "artifacts": {
    "generated": false,
    "reason": "NOT_REQUESTED"
  }
}
```

Generate files only when explicitly requested for archive or download.

## 10. Execution modes

### FULL_RAW_RUN

Prospectively maintains all available current-week and session ledgers.

### WEEKLY_SETTLED_CLOSEOUT_RAW_v1

Runs only after the Sunday CEST close and fetches/finalizes only:

- settled BTC weekly/daily source rows;
- settled ETH weekly/daily source rows;
- direct ETH/BTC weekly/daily source rows;
- Sunday settled rows and necessary preceding rows;
- ETF/IBIT session-ledger verification;
- P1 reference and terminal source observations;
- source receipts;
- raw-data readiness.

It must not repeat the full week of already preserved intraday arrays or create a new large package.

## 11. Authority

Every V6 packet must state:

```json
{
  "binding": false,
  "canonical_acceptance": false,
  "framework_state_change": false,
  "portfolio_action": false,
  "framework_interpretation": "DEFERRED_TO_MAIN_FRAMEWORK"
}
```

The Main Framework may accept source fields by field after validation. Collector interpretations have zero authority.

## 12. Activation and migration

```text
V5 remains the active source until the first complete V6 packet is reviewed and accepted.
An empty V6 thread, bootstrap acknowledgement or schema test does not supersede V5.
The first accepted V6 packet must preserve both canonical and collector predecessor lineage.
No market state, gate, event or portfolio action changes merely because V6 is prepared or activated.
```
