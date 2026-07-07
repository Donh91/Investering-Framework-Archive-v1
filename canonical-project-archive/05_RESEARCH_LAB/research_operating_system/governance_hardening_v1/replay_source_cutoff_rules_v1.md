# Replay Source-Cutoff Rules v1

Date: 2026-07-07  
Status: ACTIVE NO-HINDSIGHT SOURCE RULE  
Purpose: Define which data is allowed in state-at-time rows during replay.

---

## 1. Purpose

No-hindsight replay is only valid if each row uses only data that was available at the as-of timestamp.

This file defines the cutoff rules for DATA PING, OHLC, ETF flow, breadth, BTC.D, derivatives, stablecoin, macro and research artifacts.

---

## 2. Core rule

`State-at-time can only use data available at or before the as-of timestamp.`

Future data may only appear in outcome columns.

If availability is uncertain, mark:

`ASOF_AVAILABILITY_UNKNOWN`

Do not infer.

---

## 3. Replay row separation

Every replay row must separate:

### As-of section

- data available at time
- data missing at time
- source version
- state_at_time
- gate_status
- rebuy_status
- flow_status
- FNP_status
- next_up / next_down

### Outcome section

- forward returns
- actual high/low after as-of date
- max adverse/favorable excursion
- whether triggers occurred later
- rule_helped / rule_hurt

Outcome data cannot affect as-of classification.

---

## 4. Source cutoff rules by asset

### DATA PING rows

Allowed:

- latest DATA PING row at or before as-of timestamp
- highest active DATA PING version at that timestamp

Forbidden:

- later DATA PING rows
- lower DATA PING version if higher active version existed
- inferred state from missing DATA PING row

Labels:

- DATA_PING_ROW_AVAILABLE
- DATA_PING_ROW_MISSING
- DATA_PING_VERSION_UNRESOLVED
- DATA_PING_VERSION_CONFLICT

### BTC / ETH OHLC

Allowed:

- completed candles only for close-based logic
- intraday price only if replay row explicitly uses intraday snapshot
- source must be labeled: Binance, FMP composite, CoinGecko, etc.

Forbidden:

- using end-of-day close before daily candle completed
- using weekly high/low inside the week to classify earlier days
- mixing exchange-primary and composite without label

Labels:

- DAILY_CLOSE_FINAL
- CURRENT_CANDLE_PARTIAL
- SOURCE_COMPOSITE
- SOURCE_EXCHANGE_PRIMARY

### ETF flow

Allowed:

- finalized ETF rows only
- latest completed trading-day flow known at as-of timestamp
- pending row only as PENDING context, not scoring

Forbidden:

- placeholder 0.0 as final
- future finalized row for earlier timestamp
- pending row in trailing trend/streak windows

Labels:

- ETF_FINALIZED
- ETF_PENDING
- ETF_PLACEHOLDER_DO_NOT_SCORE
- ETF_FINALIZATION_UNKNOWN
- ETF_SOURCE_CONFLICT

### BTC.D

Allowed:

- source-labeled BTC.D at/as before timestamp
- single-source BTC.D with lower confidence label

Forbidden:

- treating single-source BTC.D as high-confidence cross-source truth
- backfilling later BTC.D

Labels:

- BTCD_SINGLE_SOURCE
- BTCD_CROSS_SOURCE_OK
- BTCD_NOT_COMPUTABLE

### ETH/BTC

Allowed:

- direct ETHBTC pair preferred
- same-source derived ETH/BTC if labeled derived

Forbidden:

- mixing ETH and BTC sources without derived warning
- using ETH/BTC >0.0275 as Rotation Confirmed

Labels:

- ETHBTC_DIRECT
- ETHBTC_DERIVED
- ETHBTC_SOURCE_MISSING

### Breadth

Allowed:

- fixed universe breadth sample with timestamp
- same-session persistence only if prior rows exist

Forbidden:

- changing token universe silently
- treating missing breadth as neutral
- using future breadth persistence

Labels:

- BREADTH_AVAILABLE
- BREADTH_DATA_MISSING
- BREADTH_UNIVERSE_UNSTABLE

### Funding / OI / derivatives

Allowed:

- timestamped funding/OI values available at as-of time
- source-labeled Binance futures data

Forbidden:

- future OI/funding in state row
- using derivatives alone to determine framework state

Labels:

- DERIVATIVES_AVAILABLE
- DERIVATIVES_DATA_MISSING
- DERIVATIVES_CONTEXT_ONLY

### Stablecoin / TVL

Allowed:

- official DeFiLlama stablecoin mcap if available
- chain distribution only as partial context
- TVL separated from stablecoin official

Forbidden:

- treating stablecoin chain sum as official total mcap
- treating TVL PASS as stablecoin PASS
- treating missing stablecoin as neutral

Labels:

- STABLECOIN_OFFICIAL_AVAILABLE
- STABLECOIN_OFFICIAL_MISSING
- STABLECOIN_CHAIN_CONTEXT_ONLY
- TVL_CONTEXT_ONLY

### CFGI sentiment

Allowed:

- current snapshot data
- history only if explicit historical export exists

Forbidden:

- inventing 24h/48h history without API/export
- using CFGI as action trigger

Labels:

- CFGI_CURRENT_ONLY
- CFGI_HISTORY_MISSING
- CFGI_SHADOW_ONLY

### FRED macro

Allowed:

- targeted FRED Classic v1.2 macro shadow status
- macro context for Master Monday calibration

Forbidden:

- FRED macro triggering rebuy, recovery, rotation, deployment, FNP or official row

Labels:

- FRED_MACRO_SHADOW
- FRED_DATA_MISSING

### Fable / Claude research artifacts

Allowed:

- research artifacts that existed at or before as-of date
- evidence registry status after ratification date

Forbidden:

- using later research to rewrite prior live state
- treating Fable output as binding without ChatGPT governance ratification

Labels:

- RESEARCH_AVAILABLE_ASOF
- RESEARCH_NOT_AVAILABLE_ASOF
- RESEARCH_NON_BINDING
- CHATGPT_RATIFIED

---

## 5. Finalization timing rules

If exact finalization timestamp is unknown:

- mark ASOF_FINALIZATION_UNKNOWN
- avoid using that data for intraday state classification
- allow use only for end-of-day or later replay if conservative

If a row is partial:

- mark CURRENT_CANDLE_PARTIAL or ETF_PENDING
- do not use as completed-close or finalized-flow evidence

---

## 6. Missing data rule

Missing data must be explicit.

Use:

- DATA_MISSING
- SOURCE_MISSING
- ASOF_UNKNOWN
- NOT_COMPUTABLE
- PARTIAL_ONLY

Do not use:

- neutral
- assumed zero
- likely unchanged
- inferred from price

---

## 7. Hindsight violation labels

Mark `HINDSIGHT_RISK` if:

- future high/low is used in state row
- future ETF row affects current flow state
- later Fable/P1b conclusion changes prior state
- final weekly actual modifies forecast interpretation
- missing data is filled from later context

Mark `HINDSIGHT_FAIL` if confirmed.

Rows with HINDSIGHT_FAIL cannot be used for rule-effectiveness scoring.

---

## 8. Recommended source-cutoff fields for replay CSV

Every replay CSV should include:

- asof_timestamp
- source_cutoff_timestamp
- data_available_at_time
- data_missing_at_time
- data_pending_at_time
- finalized_data_used
- partial_data_used
- future_data_in_outcome_only
- hindsight_check
- notes

---

## 9. Governance conclusion

Replay can only become evidence if source-cutoff discipline is preserved.

Any replay with unresolved source timing must be labeled:

`PARTIAL_REPLAY_WITH_ASOF_LIMITS`

No replay may authorize portfolio action.
