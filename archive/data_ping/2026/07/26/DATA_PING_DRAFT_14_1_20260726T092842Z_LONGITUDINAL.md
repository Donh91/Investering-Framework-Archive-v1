# DATA PING DRAFT 14.1 — 2026-07-26 09:28:42Z

Status: SHADOW / NON-BINDING  
Semantic status: PASS  
Collection status: PARTIAL  
Transport integrity: UNVERIFIED_CHAT_TRANSPORT  
Canonical state change: false  
Portfolio action: false

## Longitudinal read versus 2026-07-26 06:17Z snapshot

### Price and relative strength

- BTC CoinGecko: 64,316 -> 64,483 (+0.26%).
- ETH CoinGecko: 1,881.47 -> 1,882.93 (+0.08%).
- BTC 24h change improved from +0.51% to +1.02%.
- ETH 24h change improved from +1.29% to +1.61%.
- ETH still modestly outperformed BTC over 24h, but no direct ETH/BTC series was collected.
- BTC dominance: 56.4324% -> 56.4831% (+0.0507pp).
- ETH dominance: 9.9307% -> 9.9187% (-0.0120pp).

### ETF layer resolved

Farside latest settled session 2026-07-24:

- BTC ETF: -240.1M.
- ETH ETF: -70.7M.
- BTC latest two sessions: -465.2M.
- ETH latest two sessions: -44.4M.

This resolves the prior source block. Institutional flow is now explicitly negative across both complexes. ETH's five-session positive streak ended on 24 July.

### Flow and positioning

Settled BTC taker-buy share:

- 1h: 42.96% -> 46.70%.
- 4h: 46.02% -> 45.81%.
- 12h: 46.95% -> 46.02%.

Seller dominance therefore remained present across all windows. The 1h window improved but did not cross 50%.

BTC OI:

- 1h: -0.20% -> +0.07%.
- 4h: -0.36% -> -0.10%.
- 24h: -1.15% -> -1.02%.

Funding average remained modestly positive and nearly unchanged: 0.00003344 -> 0.00003497. Basis stayed slightly negative: -0.0359% -> -0.0393%.

Deterministic feature candidate:

`PRICE_UP_WITH_PERSISTENT_SELLER_DOMINANCE_AND_24H_DELEVERAGING`

Interpretation remains owned by the main framework. The combination is compatible with passive absorption or low-conviction recovery, but not sufficient evidence of a fresh leveraged impulse.

### Sentiment

- BTC CFGI: 48, Neutral.
- ETH CFGI: 52, Neutral.
- Global CFGI unavailable.

### Macro and liquidity

- DGS2 4.37%, DGS10 4.71%, curve +34bp.
- VIX 18.70.
- Broad USD index latest available observation remains 2026-07-17 and is temporally stale relative to the market snapshot.
- Stablecoin overview failed again with NOT_DETERMINED.
- Total DeFi TVL bounded endpoint unavailable.

### Breadth

Both top-50 pages returned, but no filtered aggregate was computed. Preview rows are not eligible as formal breadth evidence.

### Source QA

Improvements:

- PUBLIC_WEB moved to PASS.
- Farside BTC and ETH rows extracted successfully.
- Current BTC and ETH CFGI values extracted.
- Binance context marked PASS.
- Run-start timestamp captured correctly.

Remaining blockers:

- Global CFGI.
- Filtered top-100 breadth aggregate.
- Stablecoin overview.
- Bounded total DeFi TVL.
- OKX mark/index/funding/OI crosscheck.
- Direct ETH/BTC and ETH derivative context are not present in this packet despite the stronger group-level status.

## Framework state

- Rotation: NO_ROTATION.
- Rebuy: LOCKED.
- New entry: NOT_ACTIVE.
- Large caps: WATCH_ONLY.
- Recovery upgrade: none.
- Canonical state: unchanged.

## Dominant read

`PRICE_RESILIENCE_WITH_NEGATIVE_ETF_FLOW, SELLER-DOMINANT SPOT FLOW, AND 24H DELEVERAGING`

This is useful shadow evidence of absorption/resilience, but not sufficient for rotation, recovery, rebuy, deployment or portfolio-state changes.
