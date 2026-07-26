# DATA PING DRAFT 14.1 — 2026-07-26 06:17:18Z

**Status:** SHADOW / NON-BINDING  
**Semantic packet:** PASS  
**Collection:** PARTIAL  
**Transport integrity:** UNVERIFIED_CHAT_TRANSPORT  
**Canonical state change:** false  
**Portfolio action:** false

## Longitudinal comparison versus prior DRAFT 14.1 snapshot

Previous snapshot: 2026-07-25T15:23:00.457Z  
Current snapshot: 2026-07-26T06:17:18.557Z

### Market and dominance

- BTC final: 64,236.19 -> 64,353.94, approximately +0.18%.
- ETH CoinGecko: 1,867.80 -> 1,881.47, approximately +0.73%.
- BTC dominance: 56.5308% -> 56.4324%, -0.0984 percentage points.
- ETH dominance: 9.8926% -> 9.9307%, +0.0381 percentage points.
- BTC 48h return weakened from -1.02645% to -1.37836%.
- Total market cap 24h change improved to +0.7684%, while total volume contracted 36.4%.

### Flow and positioning regime shift

The largest new development is a complete reversal in settled BTC spot taker flow:

- 1h taker-buy share: 74.28% -> 42.96%.
- 4h taker-buy share: 71.02% -> 46.02%.
- 12h taker-buy share: 54.43% -> 46.95%.

Open interest also changed from a 24h build to net contraction:

- 1h OI change: +0.0566% -> -0.1977%.
- 4h OI change: -0.1129% -> -0.3580%.
- 24h OI change: +2.0437% -> -1.1484%.

Funding remained positive but cooled materially:

- latest-three average: 0.00005793 -> 0.00003344, approximately -42%.

Basis remained slightly negative but moved closer to zero:

- -0.04970% -> -0.03588%.

### Deterministic candidate classification

The combination of:

- mildly higher current price,
- declining OI,
- weaker funding,
- and taker-sell dominance across 1h, 4h and 12h

is best stored as a non-authoritative deterministic feature candidate:

`PRICE_STABLE_TO_UP_WITH_DELEVERAGING_AND_SELLER_DOMINANCE`

This is compatible with position reduction, short-covering, passive absorption or low-conviction stabilization. It is not sufficient to prove durable demand expansion.

## ETH and rotation relevance

ETH outperformed BTC over 24h and ETH dominance rose while BTC dominance fell slightly. This is supportive relative evidence, but the packet still lacks:

- direct ETH/BTC current and horizon series,
- ETH taker flow,
- ETH funding and OI,
- and settled ETH/BTC gate distances.

Therefore the packet is not eligible to confirm rotation. Existing framework state remains:

- rotation: NO_ROTATION,
- rebuy: LOCKED,
- new entry: NOT_ACTIVE,
- large caps: WATCH_ONLY.

## Sentiment caveat

ETH CFGI was returned as daily 47, 4h 34, 1h 35 and 15m 44, but its source timestamp is 2026-07-24T22:33:00Z, approximately 31 hours 44 minutes before the snapshot. It is not current-run sentiment and should be tagged `STALE_LATEST_AVAILABLE`, not treated as live.

Global and BTC-specific CFGI remain unavailable.

## Breadth caveat

Both top-50 CoinGecko pages returned, which is an improvement over the prior packet, but the filtered aggregate was not computed. The preview is not eligible for formal breadth use.

Required future fields remain:

- universe ID,
- stablecoin/wrapped exclusions,
- membership hash,
- included and excluded counts,
- advancers, decliners and unchanged,
- median return,
- BTC and ETH outperformance counts.

## Source-QA developments

### Improved

- CoinGecko top-100 raw coverage completed.
- FRED added DTWEXBGS.
- all four FRED series returned bounded histories.
- Binance finalization and freeze invariants passed.

### Still blocked or partial

- run start timestamp was not captured.
- Farside latest ETF rows were not exposed.
- global and BTC sentiment were unavailable.
- stablecoin overview failed with unknown tool failure.
- total DeFi TVL endpoint unavailable.
- ETH and ETH/BTC Binance context absent.
- OKX derivatives crosscheck incomplete.
- all receipt retrieval timestamps except a few final calls remain null.

## Framework consequence

This packet provides useful longitudinal evidence of a change from prior short-term buy-side pressure and OI expansion toward seller-dominant flow and deleveraging, while price remained comparatively stable and ETH modestly outperformed.

It does not provide sufficient evidence for:

- recovery upgrade,
- rotation confirmation,
- rebuy unlock,
- new entry permission,
- or portfolio action.

## State

```json
{
  "artifact_id": "DATA_PING_DRAFT_14_1_20260726T061718Z",
  "status": "SHADOW_NON_BINDING_PARTIAL",
  "canonical_state_change": false,
  "portfolio_action": false,
  "rotation": "NO_ROTATION",
  "rebuy": "LOCKED",
  "new_entry": "NOT_ACTIVE",
  "large_caps": "WATCH_ONLY",
  "dominant_feature_candidate": "PRICE_STABLE_TO_UP_WITH_DELEVERAGING_AND_SELLER_DOMINANCE",
  "rotation_analysis_eligible": false,
  "breadth_analysis_eligible": false,
  "etf_analysis_eligible": false,
  "sentiment_current_run_eligible": false
}
```