# DATA PING framework read — run 2c9f6a8e

```yaml
snapshot_utc: 2026-07-28T12:45:00Z
classification: STALLED_REBOUND_WITH_BREADTH_REDETERIORATION_AND_ETH_RELATIVE_WEAKNESS
source_status: PARTIAL_MARKET_USABLE_WITHOUT_DIRECT_GATE_AUTHORITY
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
backtest_effect: NONE
```

## Change since 09:55 UTC predecessor

| Field | Previous | Current | Change |
|---|---:|---:|---:|
| BTC CoinGecko | 63,470 | 63,377 | -0.15% |
| ETH CoinGecko | 1,881.43 | 1,878.20 | -0.17% |
| Derived ETH/BTC | 0.02964282 | 0.02963536 | -0.03% |
| Breadth advance ratio | 8.99% | 6.74% | -25.0% |
| OKX BTC OI USD | 2.024B | 2.057B | +1.62% |
| OKX ETH OI USD | 1.369B | 1.362B | -0.57% |

The prior weak rebound stalled. BTC and ETH both slipped, while ETH again underperformed marginally. Breadth fell from eight to six advancers among 89 included assets.

## Breadth

```yaml
included_assets: 89
advancers: 6
decliners: 71
unchanged: 12
advance_ratio: 6.74%
median_return_24h: -3.0%
outperformed_BTC: 42
outperformed_ETH: 58
membership_hash: UNAVAILABLE_LOCAL_HASH_NOT_COMPUTED
```

Breadth remains capitulatory. The missing membership hash reduces audit completeness, but the aggregate remains directionally informative and cannot be used as a hard promotion input.

## Relative strength

```yaml
ETHBTC_derived: 0.0296353567
distance_below_0_0300: -1.22%
distance_above_0_0275: +7.76%
direct_ETHBTC_available: NO
```

The derived ratio stayed below 0.0300 and faded slightly. Because direct Binance ETH/BTC was unavailable, neither the 0.0275 support gate nor the 0.0300 rotation gate can be scored from this packet.

## Derivatives cross-check

```yaml
OKX_BTC_funding_current: -0.00205%
OKX_ETH_funding_current: -0.00097%
OKX_BTC_OI_change_since_predecessor: +1.62%
OKX_ETH_OI_change_since_predecessor: -0.57%
OKX_BTC_basis_bps: -5.45
OKX_ETH_basis_bps: -4.52
```

BTC shows rising open interest with negative funding and a negative basis. This is consistent with fresh short-side or hedging pressure, but not directionally conclusive. ETH open interest fell slightly while funding remained negative, more consistent with continued deleveraging than fresh leadership.

## Missing confirmation layers

```yaml
BTC_ETF: UNAVAILABLE
ETH_ETF: UNAVAILABLE
CFGI_global: UNAVAILABLE
CFGI_BTC: UNAVAILABLE
CFGI_ETH: UNAVAILABLE
Binance_context: FAIL_GEO
Binance_final: FAIL_GEO
stablecoin_global_total: UNAVAILABLE
```

No current flow, sentiment, direct spot-taker, funding-history or settled ETH/BTC confirmation is available.

## Framework decision

```yaml
repair_structure: UNDER_PRESSURE_NOT_SETTLED_FAILED
ETH_transmission: FADING_UNCONFIRMED
breadth_confirmation: FAILED
flow_confirmation: UNAVAILABLE
settled_0_0300_confirmation: NO_EVIDENCE
rotation_permission: NO
rebuy_permission: NO
new_entry_permission: NO
portfolio_action: NONE
```

This packet does not alter frozen Backtest Wave 1 or Wave 1.1 evidence and is retained only as current-state chronology.
