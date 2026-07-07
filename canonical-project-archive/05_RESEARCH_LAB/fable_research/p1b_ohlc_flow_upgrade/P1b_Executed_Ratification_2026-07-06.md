# FABLE 5 RESEARCH — P1b EXECUTED RATIFICATION

Date: 2026-07-06  
Status: APPROVED SELECTIVE IMPLEMENTATION  
Classification: OHLC + flow-conditioned governance calibration  
Folder: `/canonical-project-archive/05_RESEARCH_LAB/fable_research/p1b_ohlc_flow_upgrade/`

---

## 1. Executive conclusion

Fable 5 P1b is accepted as an executed research artifact.

P1b materially upgrades P1 by adding:

- true OHLC / true intraday high-low data from FMP composite OHLC
- true Wilder ATR14
- Farside BTC ETF-flow ingestion, sum-verified
- flow-conditioned E3/E8 tests

P1b does **not** authorize rebuy, portfolio action, Recovery Confirmed, Rotation Confirmed or any deployment change.

Final governance stance:

- REBUY: LOCKED
- v0.2: BTC-tier state-gate only
- v0.2 can classify and measure, but cannot buy
- FNP: ledger-only measurement
- 2/3-close: governance discipline, not proven price edge

---

## 2. Data and scope

Sources:

- FMP composite OHLC, not Binance primary
- Farside BTC ETF flows, 2024-2026, sum-verified

Labels:

- E5-OHLC: OHLC-GRADE
- E3-FULL: OHLC-GRADE + PARTIAL flow-conditioned, ETF-era only
- E8-FULL: PRICE-ONLY cost + PARTIAL flow-conditioned

Important limits:

- FMP is composite OHLC, not Binance primary.
- E5/E8 use 13 pullback episodes.
- E3 flow cells are small, approximately 9-12 events.
- Flow-conditioned results are ETF-era only.
- Leverage, breadth and ETH/BTC persistence are not validated in this run.
- E8 anchors use episode-low knowledge and therefore provide expected-cost priors, not live decision signals.

---

## 3. E5-OHLC — hybrid gate integrity

Verdict: SUPPORTED.

P1b retested v0.2 hybrid integrity using true OHLC and true Wilder ATR14.

Result:

- Hybrid v0.2 beats binary v0.1.1 under close-trigger.
- Hybrid v0.2 also beats binary under wick-trigger.
- Wick-driven deaths do not reverse the hybrid advantage.

Key numbers:

- close-trigger binary: 50 deaths / 24 false deaths
- close-trigger hybrid h1.0: 28 deaths / 16 false deaths
- wick-trigger binary: 83 deaths / 46 false deaths
- wick-trigger hybrid h1.0: 53 deaths / 27 false deaths

Governance implementation:

- keep v0.2 hybrid integrity
- upgrade confidence to MEDIUM-HIGH
- v0.2 remains BTC-tier state-gate only
- v0.2 cannot buy

---

## 4. 59.0K hard-death parameter

Verdict: KEEP RATIFIED.

P1b confirms that 59.0K remains defensible, but adds a critical interpretation nuance.

At current true ATR14, 59.0K is only about 0.171 true ATR below the 59.4K shelf.

Therefore 59.0K should not be understood as a wide ATR buffer.

It should be understood as:

`one clear close below the 59.4K shelf`

Ratified rule remains:

- soft breach: close <59.4K
- hard death: 1 close <59.0K OR 2 consecutive closes <59.4K

Governance annotation added:

`59.0K is a tight hard-death, not a wide ATR buffer.`

---

## 5. E3-FULL — close-persistence doctrine

Verdict: NOT SUPPORTED as price edge.

P1b retested close-persistence with true OHLC whipsaw detection and Farside ETF-flow conditioning.

Result:

- true OHLC whipsaw detection makes the doctrine weaker, not stronger
- ETF-era N1/N2/N3 hit-rates: 0.344 / 0.44 / 0.409
- flow-conditioning does not rescue the edge
- flow-IMPROVING subset is worst in this run
- flow-NEGATIVE subset is best, though samples are small

Flow-conditioned hit rates:

- flow NEGATIVE N1/N2/N3: 0.444 / 0.5 / 0.667, n=9
- flow NONNEG N1/N2/N3: 0.455 / 0.556 / 0.375, n=11
- flow IMPROVING N1/N2/N3: 0.167 / 0.25 / 0.25, n=12

Governance implementation:

- keep 2/3-close as governance discipline only
- do not call it historically proven
- do not say flow-conditioning validated it
- add language rule:
  `ratified discipline, price-edge unproven, flow-conditioning did not rescue the edge`
- keep N <= 3
- freeze no parameter from E3

---

## 6. E8-FULL — FNP expected-cost prior

Verdict: SUPPORTED as measurement.

P1b confirms the updated FNP prior.

Result:

- METER_B median: 7.8%
- bootstrap CI: 6.6-10.3%
- p90: 11.8%
- false negative: 1/13
- flow-negative recovery median: 7.8%
- flow nonnegative/positive median: 7.1%, very small sample

Governance implementation:

- keep FNP expected-cost prior at approximately 9% [7-12]
- keep p90 at approximately 12%
- ledger-only
- not live signal
- not rebuy pressure
- not portfolio action

---

## 7. What P1b does not validate

P1b does not validate:

- breadth thresholds
- leverage thresholds
- ETH/BTC persistence
- Rotation Confirmed
- Recovery Confirmed
- rebuy
- deployment
- macro layer
- options layer

These remain outside P1b scope.

---

## 8. Final implementation row

Approved selective implementation:

1. v0.2 hybrid integrity remains active and confidence is upgraded to MEDIUM-HIGH.
2. 59.0K hard-death remains ratified, with tight-buffer annotation.
3. 2/3-close doctrine remains discipline only; price-edge unproven; flow-conditioning did not rescue edge.
4. FNP prior remains approximately 9% [7-12], p90 approximately 12%, ledger-only.
5. Rebuy remains LOCKED.
6. No portfolio action.

---

## 9. Next research priority

Do not run more broad theory research from this artifact.

If continuing Fable research, next useful steps are narrow:

1. ETH/BTC persistence test once ETH data is ingested.
2. Leverage-conditioned subsets if historical funding/OI becomes available.
3. Breadth-conditioned persistence only if reliable historical breadth becomes available.
4. Longer OHLC sample if available to challenge or strengthen E5.

Final note:

P1b is useful because it both strengthens and weakens the framework:

- strengthens v0.2 hybrid gate
- weakens overconfidence in 2/3-close persistence
- confirms FNP cost as real and material

This is the preferred type of research: governance-relevant, falsifiable, and non-actionable without separate ratification.
