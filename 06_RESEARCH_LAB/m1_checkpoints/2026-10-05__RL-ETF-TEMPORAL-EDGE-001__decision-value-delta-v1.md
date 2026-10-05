# M1 Deterministic Decision-Value Delta v1

**Mission:** `RL-ETF-TEMPORAL-EDGE-001`  
**Date:** 2026-10-05  
**Status:** VERIFIED_DELTA_FOR_SECOND_SOL_PASS  
**Authority:** RESEARCH_ONLY / NO_CANONICAL_EFFECT  
**Current main at freeze:** `2380d2c8392209e3e86d2e5b26903c3f1fefe1d4`

## Why this delta exists

The first GPT-6.1 Sol pass returned `INSUFFICIENT_EVIDENCE` because the supplied package did not contain a correct common-cutoff A1/A2 replay or post-fire outcome crosswalk.

Those missing deterministic measurements now exist.

## 1. Model-free PIT replay

Artifact:
`06_RESEARCH_LAB/m1_replay/2026-10-05__RL-ETF-TEMPORAL-EDGE-001__pit-edge-replay-v1.json`

Source ledger:
- 3,732 vintage rows
- SHA-256 `ff7be4c948492233411cfc1bf0d21c6f4fbd7a02fb359703282d4e6cbdd0dc4b`

Both replay interpretations produced the same signal fires:
- `VERIFIED_ONLY`
- `D1_START_D4_COMPLETE_REVISIONS`

Only 23 BTC sessions had admissible evidence in the observed window.

### A2
Exactly two true consecutive endpoint rows, representing one persistence episode:
- onset endpoint session: 2026-09-10
- first legally evaluable: 2026-09-11T11:12:13Z
- exact three-session values: -46.6, -120.2, -282.7m
- sum: -449.5m
- persisted on the next endpoint
- no later vintage flipped the signal after first evaluation

### A1
Exactly two true consecutive endpoint rows, representing one persistence episode:
- onset endpoint session: 2026-09-15
- first legally evaluable: 2026-09-16T11:25:33Z
- exact five-session values: -120.2, -282.7, -13.2, +159.9, -450.4m
- sum: -706.6m
- persisted on the next endpoint
- no later vintage flipped the signal after first evaluation

August candidate streaks are not official verified PIT fires because required sessions lack admissible verified evidence.

The replay includes an explicit consecutive-session guard and exact-window knowledge-time semantics.

## 2. Point-in-time outcome crosswalk

Artifact:
`06_RESEARCH_LAB/m1_replay/2026-10-05__RL-ETF-TEMPORAL-EDGE-001__decision-value-crosswalk-v1.json`

### A2 onset - 2026-09-11T11:12:13Z

Point-in-time price anchor:
- BTC 76,993.25
- owner run retrieved 11:08:54Z
- last closed bar ended 11:00Z
- run existed 3.32 minutes before signal

Pre-signal:
- BTC prior 24h: -1.1173%
- BTC prior 72h: -2.0043%
- ETH/BTC prior 5d: +2.2705%
- frozen C2 warning, ETH/BTC 5d <= -3%: FALSE
- latest live breadth before signal: 26/100 advancers
- prior-day comparable breadth: 21/100

Outcomes:
- +24h BTC: +0.4712%
- +72h BTC: +1.0166%
- +7d BTC: +1.3881%
- maximum BTC drawdown from signal anchor through +7d: -2.6305%
- maximum BTC upside through +7d: +3.7623%

### A1 onset - 2026-09-16T11:25:33Z

Point-in-time price anchor:
- BTC 76,030.01
- latest available hourly owner run before signal retrieved 07:36:23Z
- last closed bar ended 07:00Z
- this is intentionally stale rather than using a later unavailable bar

Pre-signal:
- BTC prior 24h: -1.3287%
- BTC prior 72h: -0.8442%
- ETH/BTC prior 5d: -1.0006%
- frozen C2 warning: FALSE
- latest live breadth before signal: 19/100 advancers
- comparable prior-day breadth: 33/100

Outcomes:
- +24h BTC: +0.5945%
- +72h BTC: +6.9349%
- +7d BTC: +12.6528%
- maximum BTC drawdown through +7d: -1.2695%
- maximum BTC upside through +7d: +14.9489%

Interpretation constraint:
These are two independent signal onsets, not four independent events. Persistence endpoints must not inflate N.

## 3. Historical action-authority check

The first official daily Compass archive begins on 2026-09-16. Therefore no official daily Compass freeze exists for the Sep11 A2 onset.

For the Sep16 A1 onset:
- Official Compass: `CMP-20260916-bf5b03ce2d63`
- issued: 2026-09-16T20:37:24Z
- bound main SHA: `5b691f66fe5608cd5f5bd8102d5e134003e5171d`
- `action_now = HOLD_DEFENSIVE_WAIT`
- evidence snapshot contained BTC ETF -450.4m

However, the historical `scripts/data_ping/native_handlekompas.py::action_context` at that exact bound SHA decides action from:
- health
- entry signal state
- breadth < 0.40
- ETH/BTC + breadth preparation condition

ETF flow is not referenced by `action_context`.

The frozen action WHY was:
- ETHBTC=0.031550
- TOP100_BREADTH=0.32
- ENTRY_SIGNAL=WAIT

Therefore:
- the A1 signal was a false defensive predictor in this episode;
- but there is no demonstrated direct ETF-caused action divergence in the official Compass logic;
- removing ETF from the action-context inputs would not change the historical Sep16 action function because ETF was not an input to that function.

The Decision Economics owner also explicitly forbids reconstructing economic action from status/prose for freezes predating the explicit action field.

## 4. New falsification pressure

The historical claim that A1/A2 provide high-value defensive urgency now faces two clean prospective PIT episodes:
- both were followed by positive BTC returns at 24h, 72h and 7d;
- A1 in particular preceded +12.65% BTC over 7d with only -1.27% adverse excursion;
- neither episode had frozen C2 warning already true;
- both occurred with weak breadth, so ETF may have been correlated with broad weakness without predicting BTC downside.

This does not statistically prove the signal has zero value. N=2 independent onsets is small.

It does falsify any claim that the currently observed PIT sample provides positive prospective confirmation of A1/A2 defensive value.

## Requested second-pass adjudication

Adjudicate separately:

1. **Predictive edge claim:** Do the current PIT rows support A1/A2 as a high-value defensive warning?
2. **Decision-value claim:** Did ETF add measurable action divergence or economic value beyond existing owners?
3. **Governance-value claim:** Did `URGENCY_ONLY` / zero direct action authority successfully contain false-positive cost?
4. **Role recommendation:** KEEP_URGENCY_ONLY, DEMOTE_TO_SHADOW_CONTEXT, RETIRE, or INSUFFICIENT_EVIDENCE.
5. **Research burden:** What exact prospective evidence would be required to restore a stronger claim?

Do not treat N=2 as sufficient for a global statistical rejection.
Do not reward a signal for a market move it did not predict.
Do not charge economic loss to ETF if the action function did not use ETF.
