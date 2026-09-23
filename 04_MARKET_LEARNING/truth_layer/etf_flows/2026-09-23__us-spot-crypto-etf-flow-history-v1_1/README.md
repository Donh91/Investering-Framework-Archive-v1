# US Spot Crypto ETF Flow History v1.1

**Package:** `US_SPOT_CRYPTO_ETF_FLOW_HISTORY_20260923_V1_1`  
**Supersedes for row-integrity research:** `../2026-07-26__us-spot-crypto-etf-flow-history/`  
**Coverage:** BTC 2024-01-11 to 2026-07-24; ETH 2024-07-23 to 2026-07-24  
**Authority:** research / A2 evidence candidate only

## Why v1.1 exists

The immutable v1 pack contains 11 one-cell-short rows and 26 NYSE full-closure rows that were represented as zero-flow sessions. v1.1 preserves v1 unchanged and creates a clean superseding research pack.

- 11 malformed rows are restored from the exact recovery evidence bound in the existing Codex candidate and revalidated by the ETF Temporal Integrity Lab.
- All 1,164 rows keep their original dates and fund-level values except those 11 repairs.
- The 26 exchange-closure rows are retained as evidence and explicitly labelled `NYSE_FULL_CLOSURE`.
- Real zero-flow trading sessions remain `TRADING_SESSION`.
- Trailing features are generated from `TRADING_SESSION` rows only, so a closure cannot increment an N-session window or reset a signed-flow streak.

## Timing / point-in-time firewall

This pack does **not** invent publication or finality timestamps.

Historical knowledge-time semantics are owned separately by:
`research/etf_temporal_integrity/2026-09-23/ETF_KNOWLEDGE_TIME_OWNER_DECISION_v1.json`.

The generated feature table therefore uses `knowledge_time_status=NOT_ASSIGNED_BY_ROW_INTEGRITY_PACK`. Do not treat the row date, US session close, or this archive timestamp as observed knowledge time.

## Source preservation

The manifest binds the actual bytes and SHA-256 values of all six v1 CSV partitions as they existed on the creation base. Those are the immutable readback reference, not v1's stale checksum file.

Original source identities remain:
- BTC: `Etf btc.md`, 114272 bytes, SHA-256 `73ffcff5660b34a55605121c809205b2ba341a9b822bc4047efc61a995cb91fb`
- ETH: `ETF eth.md`, 77110 bytes, SHA-256 `ac623c0bdd72213851dae67798aa461a4e3ea7e4fdea13abd4b54545edb7ed72`

## Validate and build

```bash
python 04_MARKET_LEARNING/truth_layer/etf_flows/2026-09-23__us-spot-crypto-etf-flow-history-v1_1/scripts/validate_etf_flow_history.py
python 04_MARKET_LEARNING/truth_layer/etf_flows/2026-09-23__us-spot-crypto-etf-flow-history-v1_1/scripts/build_etf_flow_features.py
```

No live ETF owner, portfolio rule, market threshold or historical frozen output is modified by this package.
