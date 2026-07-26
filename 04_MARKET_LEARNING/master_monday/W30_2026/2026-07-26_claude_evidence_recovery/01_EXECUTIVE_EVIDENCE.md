# W30 Master Monday — Executive Evidence Recovery

**Run anchor:** 2026-07-26T12:26:13Z  
**Role:** External research, recovery and challenger evidence  
**Status:** `RESEARCH_EVIDENCE_ONLY / NON_CANONICAL / NON_BINDING`

## Verified market observations at package time

- BTC live: approximately `64,517.60`.
- Settled BTC close 2026-07-25: `64,375.00` UTC and `64,344.02` CEST.
- ETH live: approximately `1,887.10`.
- ETH/BTC live: approximately `0.02926`; reported four-venue spread `0.000010`.
- BTC dominance: approximately `56.47%` on CoinGecko total-market basis.
- ETH dominance: approximately `9.94%` on the same basis.
- Market-wide CFGI: `26 / Fear` as of 2026-07-26 00:00Z.

## ETH/BTC and transmission evidence

- Fourteen settled UTC closes: `0/14` at or above `0.0300`.
- Fourteen settled UTC closes: `14/14` at or above `0.0275`.
- Last settled UTC close in package: `0.02913`.
- Live distance to `0.0300`: approximately `-2.47%`.
- Live distance to `0.0275`: approximately `+6.40%`.
- F4 was independently recomputed with parity `0.000` across the four archived comparison fields.
- Directional verdict remains `GATE_UNMET`.
- Causal attribution remains `CONFOUNDED`; the package does not promote a causal explanation.

## ETF evidence

Farside settled session 2026-07-24:

- BTC ETF total: `-240.1M USD`.
- ETH ETF total: `-70.7M USD`.
- BTC two-session total: `-465.2M USD`.
- ETH two-session total: `-44.4M USD`.
- BTC seven-session total: `+245.3M USD`.
- BTC negative streak: `2` sessions.
- ETH positive streak ended on 2026-07-24.
- Weekend 2026-07-25–26 is explicitly `NON_SESSION`, never zero-filled.

## Breadth evidence

Filtered top-100 universe after exclusions:

- Included: `80`.
- Advancers / decliners / unchanged: `58 / 13 / 9`.
- Advance ratio: `0.725`.
- Median 24H return: approximately `+0.95%`.
- Median 7D return: approximately `0.00%`.
- Share outperforming BTC over 24H: `51%`.
- Share outperforming ETH over 24H: `37%`.
- Positive share 1H / 24H / 7D: `53% / 72% / 48%`.
- Removing the five strongest positive outliers still left an advance ratio near `0.707`; breadth was not solely outlier-driven.
- Sector breadth was unavailable because no reproducible category mapping was completed.

Breadth is preserved as a separate evidence dimension and is not treated as proof of ETH/BTC transmission.

## Derivatives and leverage evidence

The research package used OKX because Binance Futures returned HTTP 451 and Bybit returned HTTP 403.

BTC:

- Funding: approximately `0.0023% per 8h`.
- OI 24H change: approximately `-1.53%`.
- Basis: approximately `-0.0578%`.
- 24H arithmetic quadrant: `PRICE_UP / OI_DOWN`.
- Global long/short account ratio: approximately `1.74`.
- Top-account ratio: approximately `1.218`.
- Top-position ratio: approximately `0.95`.

ETH:

- Funding: approximately `0.0018% per 8h`.
- OI 24H change: approximately `+2.10%`.
- Basis: approximately `-0.0546%`.
- 24H arithmetic quadrant: `PRICE_UP / OI_UP`.
- Global long/short account ratio: approximately `1.71`.
- Top-account ratio: approximately `1.258`.
- Top-position ratio: approximately `0.925`.

Venue continuity to Binance-based historical series is incomplete and must remain tagged.

## Stablecoins and liquidity

- DeFiLlama total stablecoin supply: approximately `306.79B USD`.
- 1D change: approximately `-0.03%`.
- 7D change: approximately `+0.06%`.
- 30D change: approximately `-1.66%`.
- USDT: approximately `184.29B USD`.
- USDC: approximately `73.54B USD`.
- Solana stablecoin supply was reported approximately `+8.11%` over 7D.
- Exchange stablecoin balances were missing because no free reproducible source was available.
- The package contains an internal depeg-summary conflict; see the conflict registry.

## Macro and event risk

Latest values in the package:

- DGS2: `4.37%` as of 2026-07-23.
- DGS10: `4.71%` as of 2026-07-23.
- 10Y–2Y: approximately `+36 bp` in the external package's later refresh.
- VIX: `18.70` as of 2026-07-23.
- HY OAS: `2.77` as of 2026-07-23.
- DXY Yahoo fallback: approximately `101.47` as of 2026-07-24.
- Nasdaq 100: approximately `-1.15%` on the latest session in the package.

The package marks a risk-off macro imprint on 2026-07-23 and records publication lag separately from source failure.

FOMC schedule recorded by the package:

- Meeting: 2026-07-28–29.
- Decision: 2026-07-29T18:00:00Z / 20:00 CEST.
- Press conference: 2026-07-29T18:30:00Z / 20:30 CEST.
- No SEP expected.
- Market pricing in the package: roughly `64% hold / 36% +25 bp hike`.
- FOMC remains a preregistered confound for the leading-claim window.

## Volatility and structure

The package reports compressed 48H ranges relative to 30-day median ranges:

- BTC ratio: approximately `0.54x`.
- ETH ratio: approximately `0.44x`.
- ETH/BTC ratio: approximately `0.64x`.

This is archived as a structural compression fact entering FOMC week, not as a directional prediction.

## Main-framework boundary

The package supports no automatic conclusion of recovery, rotation, altseason, rebuy, deployment or new entry. State remains governed by the main framework.