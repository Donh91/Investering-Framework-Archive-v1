# Framework read — DATA PING 15.3.3 validated non-owner

## Authority decision

`dp-run-2cdf5d87b6799342dc22` is accepted as high-quality non-owner evidence only.

- validator: PASS 69/69
- collector release identity: 15.3.3 == active packet authority 15.3.3
- method authority: PASS
- execution/freeze/orchestration: PASS
- predecessor: absent
- owner grade: false
- bounded pointer: MUST NOT ADVANCE

Active bounded owner remains `run-20260806T101439Z-79DYrv6q` / `snap-20260806T101439Z-caM8nhgy`.

## Diagnostic change vs active bounded owner

| field | active owner | current non-owner | change |
|---|---:|---:|---:|
| BTCUSDT | 64602.00 | 64892.32 | +0.4494% |
| ETHUSDT | 1903.02 | 1914.84 | +0.6211% |
| ETHBTC | 0.02946 | 0.02951 | +0.1697% |
| BTC OI | 107010.162 | 106930.378 | -0.0746% |
| ETH OI | 2295968.773 | 2279702.705 | -0.7085% |

Interpretation: price repair persists while ETH leverage is lower than the active owner. BTC OI is approximately flat. This does not resemble a broad leverage-expansion breakout.

## Breadth improvement

Same membership hash as active owner allows a clean diagnostic comparison:

- positive share: 30.34% -> 39.33% (+8.99 percentage points)
- advancers: 27 -> 35 (+8)
- decliners: 42 -> 36 (-6)
- unchanged: 20 -> 18 (-2)
- equal-weight mean: -0.4663% -> -0.2247% (+0.2416pp)

This is the clearest same-universe breadth improvement in the recent comparable sequence. It remains diagnostic because the supplied filter is v1 while the scoring owner is v1.1.

## Spot / relative flow

BTC spot taker is mixed: 1h sell-side, 4h buy-side, 12h near neutral.

ETH spot taker is also mixed: 1h buy-side, 4h sell-side, 12h near neutral.

ETHBTC spot taker is buy-side across 1h/4h/12h (62.38% / 57.29% / 53.21%), which is constructive relative-flow evidence. Futures taker ratios are >1 for BTC and ETH. ETH global long/short remains elevated at 2.0665, so relative ETH strength should still be checked for spot persistence rather than inferred from derivatives alone.

## Threshold / rotation

ETHBTC 0.02951 remains 1.6333% below 0.0300. No 0.0300 confirmation is supplied. Therefore H7/relative-transmission evidence improves, but rotation permission remains closed.

## ETF

BTC +137.6M and ETH +92.1M for 2026-08-06 are reproduced again with zero dashes and exact local tie-out. This materially strengthens provenance but does not satisfy the standing two-independent-retrieval targeted owner contract. ETF owner remains 2026-08-05 until that contract is completed or governance explicitly changes prospectively.

## Framework state

```yaml
market_phase: SELECTIVE_REPAIR_FRAGILE_TRANSLATION
risk_substate: RELATIVE_ETH_CATCHUP_WITH_BREADTH_IMPROVEMENT_DUAL_ETF_ABSORPTION_AND_LIMITED_LEVERAGE_EXPANSION_BUT_ETHBTC_BELOW_0030_AND_LINEAGE_NON_OWNER
rotation: NO_ROTATION
capital_lifecycle: WAIT
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
mid_caps: NO_NEW_RISK
small_caps: NO_NEW_RISK
microcaps: NO_NEW_RISK
operational_risk_class: DO_NOT_ADD_RISK
canonical_state_change: NONE
portfolio_action: NONE
```

## Research escalation

NO. The new information is coherent with the existing transmission-repair hypothesis and the remaining blockers are deterministic lineage/owner-validation tasks, not a knowledge gap.
