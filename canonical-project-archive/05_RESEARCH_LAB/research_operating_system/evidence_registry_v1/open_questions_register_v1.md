# Open Questions Register v1.0

Date: 2026-07-07  
Status: INITIAL OPEN QUESTIONS REGISTER  
Purpose: Track unresolved framework questions, missing data and next research tests.

This file is the standing “what is still not proven?” register. It prevents untested rules from drifting into live decision logic.

---

## Priority scale

| Priority | Meaning |
|---|---|
| P0 | Must be resolved before rebuy-readiness or deployment logic can be trusted. |
| P1 | High decision value, should be next research focus. |
| P2 | Useful calibration, not urgent. |
| P3 | Optional / future layer. |

---

## Open research questions

| ID | Question | Current answer | Why it matters | Data needed | Priority | Owner |
|---|---|---|---|---|---|---|
| OQ-E2 | Does ETH/BTC persistence validate 0.0275 / 0.0300 gates? | UNTESTED. 0.0275 = reclaim pressure only. | Rotation language depends on this. | Direct ETHBTC daily data or same-source ETH/BTC closes. | P1 | Claude/Fable after data prep |
| OQ-ROT | What separates Rotation Watch from Rotation Confirmed? | Not empirically validated. | Prevents false altseason/rotation calls. | ETHBTC, breadth, BTC.D, alt breadth, deployment proxy. | P0/P1 | Inhouse spec then Claude |
| OQ-ETF | Can ETF stabilization be frozen as formula? | UNDECIDED. Farside ingestion works. | ETF flow is main blocker in current regime. | Full Farside BTC/ETH flow, price alignment, streak and trend features. | P1 | Claude/Fable |
| OQ-E3B | Does breadth rescue 2/3-close if flow did not? | UNKNOWN. | 2/3-close rationale may rely on breadth instead of ETF flow. | Historical breadth proxy. | P2 | Data sourcing first |
| OQ-LEV | Are funding/OI thresholds decision-useful? | DATA-CONSTRAINED. | Leverage can separate squeeze from genuine repair. | Historical funding, OI, long/short, liquidation clusters. | P1/P2 | Custom GPT source search / Claude later |
| OQ-RANGE | Is Cycle Navigator weekly range better than dumb baselines? | Not systematically tested. | Core public product credibility. | Weekly forecasts, actual highs/lows, prior-week range, ATR baseline. | P1 | Inhouse first |
| OQ-SCORE | Does Cycle Navigator score correlate with actual forecast quality? | Unknown. | Prevents cosmetic track-record score drift. | Historical score, forecast, actual, regime tag. | P1/P2 | Inhouse |
| OQ-FNP-LIVE | Does FNP ledger improve decisions in live replay? | Prior supported, but not replay-tested. | Waiting cost must not become emotional pressure. | Historical/replay entries, first permitted entries, missed recoveries. | P1 | Inhouse replay |
| OQ-V02-LIVE | Would v0.2 have improved historical state calls? | Supported by E5/P1b, but not full decision replay. | Tests whether gate improved actual framework behavior. | Historical rows and actual outcomes. | P1 | Replay harness |
| OQ-STABLE | Does stablecoin supply / TVL improve regime classification? | Source-mapped only. | Could improve liquidity regime read. | DeFiLlama stablecoin + TVL aligned daily. | P2 | Claude/Fable later |
| OQ-MACRO | Should FRED/macro be part of DATA PING? | Not urgent. | Useful for broad regime, but lower direct gate value. | FRED series, DXY, yields, liquidity. | P3 | Later |
| OQ-OPTIONS | Do options/Deribit signals add value? | Not tested. | Could improve squeeze/gamma context. | Deribit options, IV, skew, OI. | P3 | Later |
| OQ-PERP | Does perp/spot wick gap provide robust signal? | Diagnostic-only today. | Could improve flush detection. | Same-time spot/perp OHLC. | P2/P3 | Later |
| OQ-DATA | Is highest DATA PING version always discoverable from archive? | Rule is active, automation reliability unknown. | Prevents stale DATA PING feed. | GitHub index + thread version manifest. | P1 | Inhouse |
| OQ-OUTPUT | Do compressed DATA PING outputs preserve state/blocker quality? | Rule exists, needs audit. | Prevents output compression hiding risk. | Sample DATA PING outputs before/after compression. | P2 | Inhouse |

---

## Current “do not freeze” list

Do not freeze these without new evidence:

- ETH/BTC 0.0275 persistence count
- ETH/BTC 0.0300 rotation-confirmed threshold
- breadth thresholds
- leverage thresholds
- ETF stabilization formula
- stablecoin / TVL liquidity trigger
- options/gamma trigger
- Cycle Navigator score methodology
- weekly range skill claim vs baseline

---

## Current “ratified but caveated” list

| Component | Caveat |
|---|---|
| v0.2 hybrid gate | Supported, but still state-gate only. Cannot buy. |
| 59.0K hard-death | Tight hard-death, not wide buffer. |
| 2/3-close doctrine | Discipline only. Price-edge unproven. Flow-conditioning did not rescue edge. |
| FNP ~9% [7-12] | Ledger-only prior, not signal. |
| Lower-half-first path row | Can fire under R3/path authority, not official v0.2 row. |
| Perp wick | Diagnostic-only. |

---

## Next best research sequence

1. Build no-hindsight replay harness using existing GitHub + uploaded archive data.
2. Run Cycle Navigator weekly range skill audit vs dumb baselines.
3. Run E2 ETH/BTC persistence test.
4. Run ETF stabilization regime study.
5. Search for workable historical funding/OI source before leverage tests.

---

## Data request needed from Custom GPT for v1.1

A-C v1.0 can start without Custom GPT.

For v1.1, Custom GPT should provide:

- latest active DATA PING version and source manifest
- DATA PING schema field list
- sample rows from latest active DATA PING
- Master Monday raw file locations
- Cycle Navigator weekly forecast/actual history
- weekly range actuals and source IDs
- any canonical Farside/BTC ETF flow paths already in GitHub

Use `custom_gpt_data_request_prompt_v1.md` for a structured request.
