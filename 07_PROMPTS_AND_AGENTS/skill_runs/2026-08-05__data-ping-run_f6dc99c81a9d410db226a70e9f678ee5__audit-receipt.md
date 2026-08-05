# DATA PING ingest receipt

- run_id: `run_f6dc99c81a9d410db226a70e9f678ee5`
- snapshot_id: `snap_84870ae0a3984d5eba1b8b6ef7b16d3c`
- snapshot_utc: `2026-08-05T12:26:16.969Z`
- collector_version: `15.2.0`
- source packet SHA-256: `a6518839af60a526b70b820fdc7627e2516452fbb5769a82aca92aea63261f65`
- accepted lane: `LATEST_BOUNDED_DATA_PING_OBSERVATION`
- previous bounded owner: `run-4e87515bde8846aa9c51`
- elapsed from previous owner: `11752.967 seconds`
- canonical predecessor advanced: `false`
- portfolio action: `none`
- operational risk class: `DO_NOT_ADD_RISK`

## Files written

1. `08_SOURCE_MATERIAL/data_ping/2026-08-05__run_f6dc99c81a9d410db226a70e9f678ee5__source-record.md`
2. `04_MARKET_LEARNING/data_ping/2026-08-05__run_f6dc99c81a9d410db226a70e9f678ee5__framework-read.md`
3. `09_SOURCE_QA/data_ping/2026-08-05__run_f6dc99c81a9d410db226a70e9f678ee5__validation.json`
4. this receipt
5. update of `02_DATA_PING/operational_handoffs/LATEST_BOUNDED_DATA_PING_OBSERVATION_v1.json`

## Material findings

- BTC +0.5064% and ETH +0.4528% versus the prior bounded owner.
- ETHBTC -0.0686% despite ETHUSD repair.
- BTC OI -0.3231%; ETH OI +0.4524%.
- ETHUSDT taker-buy shares are positive, while ETHBTC shares remain strongly below 50% across 1h/4h/12h.
- Breadth is neutral-fragile and the membership hash changed; no same-universe directional claim or scored gate is authorized.
- Current BTC ETF retrieval failed; prior verified value was not forward-filled.

## Authority

```yaml
creates_canonical_truth: false
advances_accepted_predecessor: false
changes_framework_state: false
changes_model_weights: false
creates_portfolio_action: false
changes_operational_risk_class: false
```
