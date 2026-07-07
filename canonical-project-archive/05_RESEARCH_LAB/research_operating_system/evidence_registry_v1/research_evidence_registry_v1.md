# Research Evidence Registry v1.0

Date: 2026-07-07  
Status: INITIAL GOVERNANCE REGISTRY  
Scope: Current known evidence from Fable P1/P1b, framework governance context and DATA PING archive rules.

This registry is the canonical first-pass map of which framework components have evidence, which are ratified, which remain shadow-only, and what must be tested next.

---

## Evidence grade legend

| Grade | Meaning |
|---|---|
| FULL | Tested with all required data layers for the claim. |
| OHLC-GRADE | Tested with true open/high/low/close and real ATR. |
| CLOSE-ONLY | Tested with close data only. |
| PRICE-ONLY | Tested on price behavior without full flow/breadth/leverage context. |
| PARTIAL-FLOW | Includes ETF/flow conditioning but not all market context. |
| PROTOCOL-ONLY | Method defined but not executed. |
| UNTESTED | No empirical test yet. |
| SHADOW-ONLY | May be tracked, but not allowed to drive live decisions. |

---

## Registry table

| ID | Component / rule | Evidence status | Result | Confidence | Layer | Governance status | Next test |
|---|---|---|---|---|---|---|---|
| FC-E5 | v0.2 hybrid gate integrity | OHLC-GRADE + prior close-only | SUPPORTED. Hybrid beats binary under both close-trigger and wick-trigger. | MED-HIGH | LEDGER / GOV | Ratified. v0.2 can classify and measure, not buy. | Longer OHLC sample if available. |
| FC-59K | 59.0K hard-death | OHLC-GRADE nuance | KEEP RATIFIED. Defensible but tight, about 0.171 true ATR below 59.4K shelf in P1b. | MED-HIGH | GOV | Ratified with annotation: tight hard-death, not wide buffer. | Recheck if volatility regime changes materially. |
| FC-E3 | 2/3-close persistence doctrine | OHLC + PARTIAL-FLOW | NOT SUPPORTED as price edge. Flow-conditioning did not rescue edge. | MED | GOV / LIVE language | Keep as discipline only. Ban “historically proven” language. N <= 3. | Larger OHLC + flow sample; optional breadth-conditioned test. |
| FC-E8 | FNP opportunity-cost prior | PRICE-ONLY + PARTIAL-FLOW | SUPPORTED as measurement. ~9% [7-12], p90 ~12% holds. | MED | LEDGER | Ledger-only. Not signal. Not rebuy pressure. | Larger flow-positive sample; track live outcomes. |
| FC-FNP-METERS | FNP Meter A / Meter B split | PRICE-ONLY | SUPPORTED conceptually. Meter B is verdict basis; Meter A context only. | MED | LEDGER | Active measurement architecture. | Replay framework decisions with both meters. |
| FC-REBUY | Rebuy status | Governance rule | LOCKED. No P1/P1b result unlocks rebuy. | HIGH | LIVE / GOV | Active. | Only revisit under separate rebuy-readiness evidence package. |
| FC-64K | 64K old gate | Governance archive | DEAD_LEVEL / STALE_LEVEL only. Must not reappear as active trigger. | HIGH | GOV ARCHIVE | Active restriction. | None unless old gate explicitly revalidated. |
| FC-PATH | Lower-half-first / path-weight row | Governance + shadow logic | Can fire under R3 authority, but not official v0.2 row. | MED | SHADOW / LEDGER | Active as diagnostic/path row only. | Replay against weekly ranges and actual path. |
| FC-CYCLELOW | Cycle-low freeze / dual-anchor low | Governance rule | Spot low, close-basis low and perp wick must stay separate. | HIGH | GOV | Active. | Apply in replay harness to all flush events. |
| FC-PERP | Perp wick handling | Governance rule | Diagnostic-only. Cannot set canonical cycle lows or reset timers. | HIGH | SHADOW | Active restriction. | None unless spot/perp wick-gap study runs. |
| FC-ETF | ETF stabilization formula | PARTIAL-FLOW source available | UNDECIDED. Farside ingestion works, but formula not frozen. | LOW-MED | SHADOW | Do not freeze. | Dedicated ETF regime study. |
| FC-ETHBTC | ETH/BTC 0.0275 / 0.0300 persistence | UNTESTED | Open. 0.0275 = reclaim pressure, not rotation confirmation. | LOW | SHADOW | Do not freeze. | E2 ETH/BTC persistence test. |
| FC-ROTATION | Rotation Watch / Rotation Confirmed | UNTESTED as full matrix | Open. P1/P1b does not validate rotation. | LOW | SHADOW / LIVE language | Conservative language only. | ETH/BTC + breadth + deployment + ETF/flow test. |
| FC-BREADTH | Breadth thresholds | UNTESTED | Open. No historical breadth layer validated. | LOW | SHADOW | Do not freeze. | Find reliable historical breadth proxy. |
| FC-LEVERAGE | Funding / OI thresholds | DATA-CONSTRAINED | Open. No free historical funding/OI layer in P1b. | LOW | SHADOW | Do not freeze. | Binance futures history or other source. |
| FC-STABLE | Stablecoin / TVL liquidity layer | SOURCE-MAPPED | DeFiLlama candidate, not yet decision-tested. | LOW | SHADOW | Do not use as trigger yet. | E12 liquidity feature study. |
| FC-RANGE | Cycle Navigator weekly range skill | PARTIAL actual history exists | Open. Needs systematic skill scoring vs dumb baselines. | LOW-MED | RESEARCH | Not yet ratified as quantified edge. | Weekly range replay and baseline comparison. |
| FC-CN | Cycle Navigator output layout / score | Governance / brand rule | Layout preference ratified, score methodology needs evidence registry. | MED | OUTPUT | Active formatting preference. | Connect scores to actual outcomes. |
| FC-DP-GOV | Highest DATA PING version wins | Governance rule | Active source-governance rule. | HIGH | GOV | Active. | Enforce in replay harness. |
| FC-LIVELEDGER | LIVE / LEDGER / GOVERNANCE / SHADOW separation | Governance + output compression | Active. State line and main blocker must never be compressed away. | HIGH | OUTPUT / GOV | Active. | Audit future DATA PING outputs. |
| FC-CUSTOMGPT | Custom GPT sensor role | Governance architecture | Custom GPT = data collector/sensor, not final governance. | HIGH | SYSTEM | Active. | Require structured source/status output. |
| FC-CLAUDE | Claude/Fable research role | Governance architecture | Claude = research lab/adversarial executor, non-binding. | HIGH | SYSTEM | Active. | Use only narrow execution prompts. |
| FC-GPT | ChatGPT governance role | Governance architecture | ChatGPT = final framework/governance ratifier. | HIGH | SYSTEM | Active. | Maintain evidence registry and archive. |

---

## Immediate implementation changes from registry

1. v0.2 hybrid gate remains ratified and confidence is upgraded to MEDIUM-HIGH.
2. 59.0K remains hard-death, with tight-buffer annotation.
3. 2/3-close remains a discipline rule only. It is not a proven price edge and flow-conditioning did not rescue it.
4. FNP prior remains approximately 9% [7-12], p90 approximately 12%, ledger-only.
5. ETF, ETH/BTC, leverage and breadth remain open research items.

---

## Canonical language patches

Use:

`2/3-close = ratified discipline, price-edge unproven, flow-conditioning did not rescue the edge.`

Use:

`59.0K = tight hard-death / one clear close below 59.4K shelf, not wide ATR buffer.`

Use:

`FNP ~9% [7-12], p90 ~12%, ledger-only, not signal.`

Use:

`v0.2 can classify and measure, but cannot buy.`

Do not use:

- historically proven close-persistence edge
- flow-confirmed close-persistence edge
- recovery confirmed from P1/P1b
- rotation confirmed from P1/P1b
- rebuy readiness from P1/P1b
