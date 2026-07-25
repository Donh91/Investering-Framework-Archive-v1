# OTA PING #21 — SHADOW / NON-BINDING · v2-format

**Run anchor:** 2026-07-25 08:03:23 CEST / 06:03:23 UTC  
**Binance serverTime:** 1784959403585  
**Canonical state change:** false  
**Portfolio action:** false  
**New entry permission:** false

## Source QA

- Price probes: CURRENT_RUN_FRESH.
- No byte-identical price payloads versus OTA Ping #20.
- Four venues remained in parity with the 1m reference; cross-venue spread 0.096%.
- Farside `/btc/` and `/eth/`: PAYLOAD_GENERATION_FRESHNESS FAIL because footer showed 24 July on 25 July.
- BTC/ETH ETF rows for 24 July therefore remain QUARANTINED and must not be interpreted as zero or not published.
- Self-caught H7 script defect: a hardcoded leader count printed 1 instead of computed 2 of 3; corrected before final reporting.

## New and matured evidence

### F4 fully settled

- 10/10 rows settled on both SETTLED_UTC and SETTLED_CEST bases.
- Zero closes >= 0.0300 on both bases.
- Maximum occurred on day 1: 0.02961 UTC / 0.02965 CEST.
- Window change: -1.99% UTC / -2.33% CEST.
- Minimum shortfall to gate: 1.18%.
- Primary directional score: `GATE_UNMET`.
- Result was invariant across both candidate bases and venues.
- Causal interpretation remains `CAUSAL_LABEL_CONFOUNDED_BY_FLOW_REVERSAL`; the gate outcome itself is not blocked.
- Canonical preregistration text remains locally unavailable and is requested from the main framework.

### F1 lineage probable resolution

A frozen Jul-14 OTA case card contains the preregistered threshold `$62.2K truth-layer`, tied to the 13 July close and frozen before the window opened. The later 62,342 refinement remains provenance-unresolved. This is `PROBABLE_RESOLUTION`, not proven canonical lineage.

Status under both thresholds: not failed, day 5 of 7.

### Leading-claim kill criterion located

The same case card states that 2 of the first 3 prospective pre-registered S2/S3 cases failing durability at the 12-session mark retires the LEADING claim. The Jul-14 case therefore matures around 2026-07-30. FOMC 28–29 July was preregistered as a confound. No retirement decision is made from F4.

### ETH ETF 23 July dual truth compatible

- Local execution: +26.3M verified.
- Main framework archive: +26.3M officially verified.
- Compatibility: exact match.
- Leadership rotated from ETHA on 22 July to FETH on 23 July while total flow fell 64%.
- ETH ETF: 5 consecutive positive sessions from 17–23 July; 7-session sum +237.1M.

### H7 row 3 settled

24 July CEST:

- BTC: 64,155.00
- ETH: 1,857.51
- ETH/BTC: 0.02896
- BTC 1D: -1.56%
- ETH 1D: -1.34%
- Spread: +0.22pp
- Leader: ETH

H7 conditions:

- Positive log-slope in 3 successive settled rows: NO.
- ETH leads in at least 2 of last 3: MET, 2/3.
- Complete reproducible rows: MET.
- State: `INSUFFICIENT_ROWS_3_OF_5_AND_PRIMARY_SLOPE_CONDITION_NOT_MET`.

## H7 row 3 receipts

```json
{"2026-07-24|BTCUSDT":{"receipt_id":"OTA21-BTCUSDT-20260724-07","source_url_or_action":"https://data-api.binance.vision/api/v3/klines","request_parameters":"symbol=BTCUSDT&interval=1h&startTime=1784926800000&limit=1","retrieved_at_utc":"2026-07-25T06:04:24.831+00:00","raw_candle_open_time":"2026-07-24T21:00:00+00:00","raw_candle_close_time":"2026-07-24T21:59:59.999000+00:00","raw_close":"64155.00000000","raw_row_sha256":"fc3649a79a0b550e72e207f13c569c2b8e137f9622f17b55da50b045dc78f7b1","response_sha256":"756f9a9b7eabf1a26ee83262e2c315cdf3a47c8f7f1941976272b5a512478b9e","row_status":"SETTLED_PROSPECTIVE_VALID","session_basis":"SETTLED_CEST"},"2026-07-24|ETHUSDT":{"receipt_id":"OTA21-ETHUSDT-20260724-08","raw_close":"1857.51000000","raw_row_sha256":"d0755988f6b85062c90d7caac3372d7d0ac41bce7da0d45e26e4b2ca3ddd8cd7","response_sha256":"355c6d58eec54c71b128cceea0133d9cf2ef9765b26480ce94e2916b0c5ea36d","row_status":"SETTLED_PROSPECTIVE_VALID","session_basis":"SETTLED_CEST"},"2026-07-24|ETHBTC":{"receipt_id":"OTA21-ETHBTC-20260724-09","raw_close":"0.02896000","raw_row_sha256":"628b21b265ad2ac702caf91bc78277323e35bdab50d2ef13efb643c0848673ef","response_sha256":"416635489d0d82794868b773093c2608423297aca19f33bbd529559e68a15899","row_status":"SETTLED_PROSPECTIVE_VALID","session_basis":"SETTLED_CEST"}}
```

## Blocked items

- BTC ETF 24 July and ETH ETF 24 July: stale payload generation.
- F5 second negative session: depends on fresh 24 July ETF print.
- CFGI.io series: endpoint unavailable.
- W30 start-measurement venue: Coinbase probable, not proven.
- 62,342 provenance: unresolved.
- F4 canonical preregistration text: unavailable locally.

## Unchanged framework states

- F5: TRIGGERED_PROSPECTIVELY; second session undetermined.
- F1: NOT_FAILED under either threshold; day 5 of 7.
- Load-bearing 0.0275: HOLDS; full F4-window minimum 0.02873.
- Leading claim: deferred to own 12-session kill test around 2026-07-30.
- Low-vol pullback: FRAGILE / NO_INTERPRETIVE_WEIGHT.
- Rotation: NO_ROTATION.
- Rebuy: LOCKED.
- New entry: NOT_ACTIVE.
- Large caps: WATCH_ONLY.

## Next exact event

2026-07-26T00:00:00Z — low-vol 3D maturity.
