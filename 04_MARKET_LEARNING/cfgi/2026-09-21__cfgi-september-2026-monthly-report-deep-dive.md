# CFGI September 2026 Monthly Report - Deep Dive

**Date logged:** 2026-09-21  
**Status:** SHADOW MARKET-LEARNING NOTE  
**Source:** https://cfgi.io/crypto-market-monthly-report/#september-2026  
**Source state:** RUNNING MONTH, not final. CFGI updates the page daily.  
**Framework authority:** Context / calibration only. No market-state, threshold, model-weight or portfolio-execution authority.

## Executive verdict

September 2026 adds useful evidence, but it does **not** justify a new engine or a canonical threshold change.

The highest-value observation is a **quality-vs-participation divergence**:

- price and technical structure are strong;
- the aggregate monthly CFGI score remains only modestly positive;
- social, search-trend, whale and order-book components remain materially weaker than technicals;
- ETH is outperforming BTC month-to-date;
- current framework state is already `PREPARE`, with strong Top-100 breadth, but the official entry signal is still `WAIT`.

Interpretation:

> September looks more like an improving / broadening market that is not yet euphoric than a mature sentiment blow-off.

This is supportive of readiness and rotation surveillance, not standalone deployment confirmation.

---

## 1. Frozen source snapshot used for this note

CFGI Crypto Market September 2026, retrieved 2026-09-21:

- total crypto market cap performance: **+12.5%** month-to-date
- market cap high: **$2.96T**
- market cap low: **$2.59T**
- average market CFGI: **56 / Neutral**
- current 21 Sep reading reported by page: **67**
- sentiment high: **69 / Greed**
- sentiment low: **47 / Neutral**
- largest daily market-cap move: **+5.7% on 21 Sep**
- largest sentiment move: **+13 points on 18 Sep**

Monthly component averages:

- Price: **61**
- Volatility: **51**
- Volume: **50**
- Momentum: **55**
- Technical: **65**
- Social: **47**
- Dominance: **58**
- Trends: **42**
- Whales: **41**
- Orders: **49**

Important source caveat:

The report is live and changed during retrieval. These values are a point-in-time snapshot, not the final September record.

---

## 2. Month-on-month component shift vs August

August 2026 aggregate CFGI:

- average sentiment: **55**
- market-cap performance: **+18.7%**
- Technical: 55
- Social: 53
- Dominance: 46
- Trends: 58
- Whales: 55
- Orders: 52

September through 21 Sep:

- average sentiment: **56**
- market-cap performance: **+12.5%**
- Technical: **65**
- Social: **47**
- Dominance: **58**
- Trends: **42**
- Whales: **41**
- Orders: **49**

The notable change is not the composite score, which is almost unchanged.

The notable change is the **internal composition**:

- Technical strength rose sharply.
- Dominance / rotation signal strengthened.
- Social participation weakened.
- Search interest weakened materially.
- Whale activity weakened materially.
- Order-book pressure remained close to neutral.
- Volatility and volume cooled relative to August.

This is exactly the kind of evidence that should be studied through **component dispersion**, rather than treating the headline 56 as the signal.

---

## 3. BTC vs ETH monthly divergence

CFGI September 2026 through 21 Sep:

### BTC
- price performance: **+3.9%**
- average sentiment: **56**
- Technical: 65
- Social: 46
- Dominance: 59
- Trends: 40
- Whales: 37
- Orders: 47

### ETH
- price performance: **+8.2%**
- average sentiment: **59**
- Technical: 67
- Social: 48
- Dominance: 57
- Trends: 44
- Whales: 50
- Orders: 57

Bounded observation:

- ETH has outperformed BTC by about **4.3 percentage points** month-to-date.
- ETH monthly sentiment average is about **3 points above BTC**.
- ETH order-book and whale components are materially stronger than BTC's in the same running month.

This is directionally consistent with growing ETH-relative participation.

It is **not**, by itself, proof of durable rotation.

---

## 4. Alignment with current canonical framework state

Latest inspected Native Handlekompas run on 2026-09-21:

- `NOW = PREPARE`
- `ETHBTC = 0.032050`
- `TOP100_BREADTH = 0.84`
- `ENTRY_SIGNAL = WAIT`
- no active data blocker in the inspected 19:20 UTC run

This matters because the CFGI monthly report is not introducing an isolated bullish story.

It is **congruent with** a framework state that already shows:

- stronger ETH-relative conditions,
- strong breadth,
- higher readiness,
- but no canonical entry authorization.

Therefore the correct integration is:

> CFGI September strengthens PREPARE confidence and rotation-surveillance quality, while leaving DEPLOY / top-up authority unchanged.

---

## 5. Most important framework learning

### A. Headline CFGI is too compressed for this regime

A market-cap gain above 10% and strong technicals coexist with only a 56 average composite.

The composite alone hides the useful structure.

The research value is in:

- component dispersion,
- component velocity,
- BTC-vs-ETH differences,
- cross-timeframe disagreement,
- and interaction with framework regime state.

This directly supports existing `AT-HYP-0011`:

> CFGI likely has more value as a feature family than as a raw sentiment threshold.

### B. Technical strength is ahead of crowd participation

September's strongest component is Technical at 65.

Meanwhile:

- Social = 47
- Trends = 42
- Whales = 41
- Orders = 49

This is a useful **participation-gap** observation.

It can be read two ways and therefore must remain shadow-only:

1. constructive: price/structure has room before mass euphoria;
2. cautionary: the move is not yet fully confirmed by deeper participation.

The framework should not choose one interpretation from CFGI alone.

### C. Dominance component improved, but must not be confused with canonical BTC.D

CFGI defines its dominance family as a rotation-related sentiment input.

It is not the same object as the framework's canonical BTC dominance series.

Therefore:

- use it as a supporting rotation feature;
- never substitute it for BTC.D;
- never promote it to a hard rotation gate.

### D. Current strength is not sentiment euphoria

September's sentiment high is 69, below August's 78 market high and far below the historical greediest-month averages.

This supports a bounded conclusion:

> Current strength is not yet accompanied by broad, persistent extreme-greed conditions.

That does **not** imply that price must continue higher.

CFGI itself reports weak next-day forecasting power for the composite score.

---

## 6. Research and calibration relevance

### Keep active

Use this report as a monthly compression / audit layer for:

- CFGI component dispersion
- MARKET vs BTC vs ETH divergence
- sentiment velocity
- participation gap
- rotation-quality context
- pullback / recovery sequence review
- Monthly AI Learning Council
- Research Lab feature evaluation

### Candidate derived observations

Do not hard-code thresholds yet.

Track prospectively:

1. `TECHNICAL_MINUS_PARTICIPATION_GAP`
   - compare Technical against Social / Trends / Whales / Orders.

2. `ETH_VS_BTC_CFGI_PREMIUM`
   - compare ETH vs BTC aggregate score and component profile.

3. `CFGI_ROTATION_CONGRUENCE`
   - compare CFGI dominance/rotation component with canonical ETH/BTC, BTC.D and breadth.

4. `CFGI_EUPHORIA_ABSENCE`
   - strong price / technical state with composite sentiment below extreme-greed territory.

These are research features, not execution rules.

---

## 7. What this does NOT justify

Do not:

- create a new CFGI engine;
- change existing market-state thresholds;
- let monthly CFGI override DATA PING;
- treat score 56, 67 or 69 as a buy signal;
- replace BTC.D with CFGI dominance;
- label broad altseason from this report alone;
- change portfolio execution.

CFGI remains a **shadow sentiment owner**.

---

## 8. Final classification

**Relevance:** HIGH for research/calibration, MEDIUM for current-state confirmation, LOW as standalone forecast.

**Framework effect:**  
`PREPARE confidence +`  
`ROTATION_SURVEILLANCE +`  
`DEPLOY authority = unchanged`

**Archive action:** Keep this note as a point-in-time September 2026 research snapshot. Re-evaluate after the month closes so the final September row can be compared with this running-month snapshot.

## Source / governance references

- CFGI Crypto Market Monthly Report, September 2026
- CFGI Bitcoin Monthly Report, September 2026
- CFGI Ethereum Monthly Report, September 2026
- CFGI methodology: ten components, refreshed across timeframes
- `research/data_architecture/CFGI_COLLECTION_POLICY_v2.md`
- `04_RESEARCH_LAB/auto_trading/THEORY_LEDGER.md` - AT-HYP-0011
- `canonical-project-archive/05_RESEARCH_LAB/research_operating_system/governance_hardening_v1/data_ping_version_manifest_v1.md`
- `04_MARKET_LEARNING/handlekompas/runs/2026/09/21/192023_74ac4a39885a.json`
