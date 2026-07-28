# BACKTEST WAVE 1.1 — CHATGPT CONTROLLED TEST WAVE

```yaml
run_date: 2026-07-28
source_package: DATA PING BACKTEST HISTORY PACK 20260727T052808Z.zip
source_sha256: 303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f
tdbc_package: TDBC v1 TechDev Business Cycle 2026-07-26(1).zip
tdbc_sha256: e83d3b95e94fba331767feae92bd052ed7f752a1a5305d63621030b293bc5d4c
final_holdout_start: 2026-04-26
final_holdout_opened: NO
canonical_state_change: NONE
portfolio_action: NONE
```

## 1. Actual owner-policy replay

**Verdict:** `BLOCKED_OWNER_EVENT_AND_POLICY_LEDGER_INCOMPLETE`

Three owner events were visible. None had the complete combination of reconstructable state, actual policy definition, transaction-cost basis and execution timestamp required for an honest owner-policy replay.

No proxy result is allowed to change the rebuy rule.

## 2. Leave-one-cycle-out halving-orthogonalized TDBC

**Verdict:** `NOT_SEPARABLE_FROM_HALVING_CLOCK_SMALL_N`

Only three mature post-halving first-positive TDBC events could be tested under bar-end authority and next-day entry.

- Positive residual versus matched halving-clock controls: 66.7%
- Mean residual: +22.5%
- Median residual: +148.3%

The event residuals were strongly inconsistent across cycles. The 2010 event is pre-first-halving and cannot be matched honestly. The 2026 event is unmatured.

TDBC remains a descriptive research layer, not an independent promoted signal.

## 3. Episode-level drawdown hazard

**Verdict:** `NO_EPISODE_LEVEL_OOS_VALIDATION`

- Underwater episodes in source history: 97
- Episodes contributing 30/60/90/180/270-day landmarks: 19
- Landmark rows: 52
- Unconditional Brier score: 0.2485

Every tested depth/age model performed worse than the unconditional baseline in leave-one-episode-out evaluation. The best row in the table is `UNCONDITIONAL_BASELINE` with Brier 0.2485.

Claude's depth × underwater-age idea remains interesting descriptively, but is not ready for Pullback policy use.

## 4. Beta-neutral broad-alt rotation

**Verdict:** `H7_NEGATIVE_BROAD_ROTATION_003_INCONCLUSIVE_SMALL_N`

The portfolio used prior-day top-50 quote-volume membership, equal weighting and a lagged 60-day beta hedge against BTC.

### H7-like events

- Events: 48
- Median beta-neutral return:
  - 5D: -1.34%
  - 10D: -2.16%
  - 20D: -6.21%
  - 30D: -9.44%

### Direct 0.0300 first crossings

- Events: 8
- Median beta-neutral return:
  - 5D: -1.56%
  - 10D: +0.58%
  - 20D: -2.86%
  - 30D: -4.01%

H7 does not identify broad, tradable alt rotation. Direct 0.0300 crossings remain too few and too uncertain to prove broad rotation. A relative ETH/BTC event may still be meaningful for ETH without being a broad-alt deployment event.

## 5. Purged and embargoed walk-forward

**Verdict:** `NO_LINEAR_OOS_EDGE_ETF_NOT_INCREMENTAL`

The final 90-day holdout was excluded and not scored. Features were lagged one day. Training labels were purged by the full target horizon.

### BTC 5-day target

- Price-only OOS R²: -0.690
- Price + ETF OOS R²: -0.891
- Price-only sign accuracy: 48.5%
- Price + ETF sign accuracy: 49.2%

ETF features did not add predictive value in this linear, purged specification.

### ETH/BTC 20-day target

- Price-only OOS R²: -1.192
- Price-only sign accuracy: 38.0%

Breadth and dominance improved R² slightly relative to price-only, but every tested model remained materially negative out of sample.

## Governance

```yaml
owner_policy_rule_change: NONE
TDBC_promotion: NO
drawdown_hazard_policy_use: NO
H7: EARLY_ALERT_ONLY
direct_0_0300: RELATIVE_STRENGTH_CHALLENGER_NOT_BROAD_ROTATION_PROOF
ETF_flow: DESCRIPTIVE_CONFIRMATION_NOT_LINEAR_PREDICTOR
sensor_counting: DEPENDENCY_CLUSTER_AWARE
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
canonical_state_change: NONE
portfolio_action: NONE
```
