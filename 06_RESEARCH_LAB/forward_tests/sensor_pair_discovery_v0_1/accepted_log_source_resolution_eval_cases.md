# Accepted-Log Source Resolution Eval Cases

## E1 — Direct thread available

- Direct latest complete V4 payload available.
- Accepted-log pointer also valid.
- Expected: `DIRECT_PROJECT_THREAD`; accepted log retained as fallback only.

## E2 — Direct thread unavailable, accepted log valid

- Direct cross-thread access unavailable.
- `latest_accepted_log_state.json` says `READY_ACCEPTED_LOG`.
- Receipt, payload, run ID, timestamp and hash validate.
- Age <36h.
- Expected: `ACCEPTED_LOG_RECEIPT`; field-level pair eligibility.

## E3 — Bare run ID only

- Event registry exposes `DATA_PING_V4_...` but no receipt/payload hash.
- Expected: accepted-log fallback rejected.

## E4 — Receipt hash mismatch

- Receipt exists but normalized payload hash differs.
- Expected: `BLOCKED_SAFETY`; no new rows.

## E5 — Empty V5 thread, valid V4 receipt

- V5 exists but contains no complete user-supplied DATA PING.
- V4 accepted log is valid.
- Expected: V4 remains active.

## E6 — Older V3 receipt is newer by ingestion time

- V3 accepted later than V4 but V4 has already been used.
- Expected: version regression blocked; V4 remains active.

## E7 — Partial accepted packet

- ETH/BTC, breadth and OI/funding available.
- ETF, stablecoin, DEX, sentiment and A/C fields missing.
- Expected: evaluate each P01-P08 independently; do not mark missing fields negative.

## E8 — Outcome already known before freeze

- Accepted receipt arrives after the complete 24h path is already available to the runner.
- Expected: no 24h forecast row; receipt may be used as maturity input only where causally valid.

## E9 — Same version and timestamp, different hash

- Two V4 packets share timestamp but differ in content.
- Expected: `SOURCE_CONFLICT`; preserve both; no live pointer replacement.

## E10 — Full thread handoff valid, accepted log invalid

- Direct thread unavailable.
- Accepted-log hash fails.
- Exact thread-derived handoff validates.
- Expected: `THREAD_DERIVED_HANDOFF`; record accepted-log failure.

## E11 — No valid route

- Direct thread unavailable.
- Accepted log invalid or stale.
- Thread handoff invalid or stale.
- Expected: `SOURCE_UNAVAILABLE`; no forecast rows and no external substitution.

## E12 — Duplicate source hash

- Same accepted packet already processed.
- Expected: zero new forecasts; due rows may mature; duplicate count increments.
