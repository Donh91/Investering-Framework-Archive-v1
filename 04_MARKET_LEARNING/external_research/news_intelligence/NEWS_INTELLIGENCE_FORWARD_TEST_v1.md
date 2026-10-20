# NEWS INTELLIGENCE FORWARD TEST v1

**Date:** 2026-10-07  
**Status:** ACTIVE_SHADOW_FORWARD_TEST  
**Authority:** RESEARCH_ONLY_NON_CANONICAL  
**Parent:** NEWS INTELLIGENCE & SITUATION ANALYSIS RESEARCH LAB v1

## Purpose

Prospectively test whether structured news interpretation improves Situation Room / external-news intelligence versus simple headline polarity and immediate price reaction.

## Frozen baselines

### B0_HEADLINE_POLARITY
Uses only headline language.

### B1_VERIFIED_FACT_IMMEDIATE_REACTION
Uses source verification plus immediate market direction.

### B2_NEWS_EVIDENCE_CARD
Uses:
verification,
surprise,
regime,
transmission map,
cross-asset footprint,
reaction-vs-background-volatility,
persistence,
falsifiers.

## Frozen horizons

Default:
- T+4H
- T+24H
- T+3D
- T+7D

Optional slow-thesis horizons must be declared at T0:
- T+30D
- T+90D
- T+180D

## Minimum evidence before any promotion

50 prospective events.

At least:
- 10 macro/policy;
- 10 crypto/regulatory;
- 10 geopolitical/energy;
- 10 corporate/market-structure/analyst-warning;
- 10 unrestricted.

## Row immutability

T0 interpretation, channels, falsifiers, confidence and horizons are frozen.

Only outcome fields may be appended later.

No hindsight rewriting.

## Evaluation metrics

1. FACT_VERIFICATION_ACCURACY
2. FALSE_SOURCE_ADMISSION_RATE
3. FALSE_ESCALATION_RATE
4. MATERIAL_EVENT_MISS_RATE
5. DIRECTIONAL_USEFULNESS_BY_HORIZON
6. CONFIDENCE_CALIBRATION
7. TIME_TO_CORRECTION
8. CAUSAL_OVERREACH_COUNT
9. B2_VS_B0_DELTA
10. B2_VS_B1_DELTA

## Promotion rule

No canonical or execution promotion unless B2 demonstrates material prospective value over B0 and B1.

## Kill / simplify rule

At N=50:
- retire fields that cannot be populated reliably;
- retire fields with poor reviewer consistency;
- simplify if B2 does not beat B1;
- preserve only the components with demonstrated decision/context value.

## First live row

`NEWSFT-20261007-001` - Michael Burry stock-market "denial / crash" warning.
