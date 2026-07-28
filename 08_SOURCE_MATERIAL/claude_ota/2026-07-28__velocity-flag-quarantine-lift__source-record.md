# Claude OTA source record

```yaml
record_type: EXTERNAL_AUDITOR_OTA_INPUT
source_model: Claude
received_by_main_framework: 2026-07-28
source_snapshot_utc: 2026-07-28T17:38:10Z
source_snapshot_cest: 2026-07-28T19:38:10+02:00
run_type: VELOCITY_FLAG_WITH_QUARANTINE_LIFT
binding_authority: NON_BINDING_EXTERNAL_INPUT
canonical_state_change_authority: NONE
portfolio_action_authority: NONE
```

## Source narrative

No preregistered item had matured. The run was issued as a velocity flag and attempted to lift the quarantine on the 2026-07-27 Farside ETF rows.

Claude reported both Farside pages as fresh with footer date 28 July and lifted both quarantines:

- BTC ETF 2026-07-27: -11.6 million USD
  - IBIT: -8.8
  - FBTC: -2.8
  - BTCO: not reported
- ETH ETF 2026-07-27: +11.7 million USD
  - ETHA: +11.7

Multi-session flow sums reported by Claude:

| Window | BTC ETF | ETH ETF |
|---|---:|---:|
| 1 session | -11.6 | +11.7 |
| 3 sessions | -476.8 | -32.7 |
| 5 sessions | -204.5 | +77.5 |
| 7 sessions | +154.6 | +152.2 |

Claude interpreted this as the third consecutive negative BTC ETF session, while noting that the negative magnitude had contracted by approximately 95 percent from -240.1 to -11.6. F5 remained triggered from 2026-07-23 and was not retriggered. Stage-1 leg c, defined as seven-day BTC ETF flow greater than -0.5 billion USD, remained met.

Claude reported an AUM-normalized seven-session flow estimate of:

- BTC: +0.301 percent
- ETH: +1.356 percent
- ETH/BTC relative normalized flow multiple: approximately 4.5x

Claude therefore weakened, but did not reverse, the previous statement that H7 was price-led rather than flow-supported. The ETH three-session sum remained negative and the one-session inflow was materially smaller than the 2026-07-22 inflow.

## Source-QA self-falsification

Claude explicitly withdrew an earlier deterministic edge-node hypothesis for Farside freshness. The hypothesis had asserted that specific Cloudflare edge ranges reliably separated fresh and stale payloads. A fresh payload was now observed from the same 172.71/16 range as a previously stale payload.

The source record therefore supports the narrow conclusion:

```yaml
edge_node_deterministic_freshness_rule: FALSIFIED
```

Claude proposed a broader time-of-day explanation based on the Farside publication schedule and recommended querying after approximately 16:00 UTC rather than during early European morning hours. This operational scheduling rule remains a research hypothesis until supported by a prospective timing ledger.

## Experiment and design observations

- No matured score was changed.
- H7 row 7 was pending settlement at 2026-07-28T22:00:00Z.
- F1 remained `NOT_FAILED__WINDOW_CLOSED__SCORE_FINAL`.
- Claude observed that BTC printed an intraday low of 62,742.47 on 2026-07-28, one session after the F1 evaluation window closed, bringing price closer to the 62,200 threshold than any low inside the frozen window.
- This was logged as a window-design observation only and not as a rescore.
- ETH/BTC was reported near 0.02983 at the Claude snapshot, with an intraday high of 0.03010.
- Claude described this as the third consecutive session touching at least 0.0300 intraday while closing below on a settled basis.

## Source QA and cache observations

Claude reported:

```yaml
cache_guard: CURRENT_RUN_FRESH
venues_checked: 4
identical_payloads: 0
one_minute_reference_age_seconds: 10
reported_deviation_range_pct: [-0.105, -0.002]
```

The source record did not include the four venue identifiers, payload hashes, exact per-venue timestamps or row-level deviation calculations. Those details remain required for full independent replay.

## Unverified queue preserved from source

- BTC ETF 2026-07-28
- ETH ETF 2026-07-28
- F1 threshold attribution
- CFGI.io series
- W30 start venue, Coinbase probable
- provenance of 62,342
- F4 canonical preregistration text

## Unchanged experiment states reported by Claude

```yaml
F1: NOT_FAILED__WINDOW_CLOSED__SCORE_FINAL
F4: GATE_UNMET__SCORED__CLOSED
F5: TRIGGERED__THIRD_NEGATIVE_SESSION_OBSERVED__NOT_RE_TRIGGERED
H7: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION__ROW7_PENDING
low_vol_pullback: FRAGILE__SERIES_COMPLETE__NO_PROMOTION
load_bearing_0_0275: HOLDS
leading_claim: RETIREMENT_DEFERRED_TO_12_SESSION_KILL_TEST__FOMC_CONFOUND_ACTIVE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: false
portfolio_action: false
new_entry_permission: false
```

## Temporal relationship to main DATA PING

The immediately preceding accepted DATA PING snapshot was frozen at `2026-07-28T17:12:27.297Z`. Claude's OTA snapshot was approximately 25 minutes and 43 seconds later. Differences in live ETH/BTC or venue prices therefore do not constitute a source conflict by themselves.

This external OTA output was not available to the main framework at the knowledge time of the first prospective A-class receipt and must not be retroactively inserted into that receipt.