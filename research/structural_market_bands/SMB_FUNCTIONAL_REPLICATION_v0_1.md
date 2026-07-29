# SMB FUNCTIONAL REPLICATION v0.1

Status: RESEARCH_ONLY
Date opened: 2026-07-29
Authority: Shadow research, zero Core or portfolio authority
Objective: Determine whether a reproducible Structural Market Bands proxy adds incremental value for BTC structural support, resistance and range placement beyond simple on-chain and price baselines.

## 1. Research question

Can the public description of Alphractal Structural Market Bands be translated into transparent, causal proxies that improve:

- structural support and resistance placement
- downside-depth calibration
- post-flush classification
- 5–7d and multi-week range placement
- accumulation/protection context

without relying on the proprietary formula or retrospective chart fitting?

## 2. Publicly supported claims

The public description states that SMB:

- uses 100% on-chain data
- is designed for UTXO-type blockchains
- combines reliability of lifespan data with short-, medium- and long-term market-cap movements
- produces structural support and resistance zones
- interprets penetration as counter-pressure/potential rather than automatically flipping support into resistance

These claims are hypotheses to operationalize, not accepted performance claims.

## 3. Non-goals

- Do not claim exact reverse engineering.
- Do not infer hidden proprietary parameters as facts.
- Do not use SMB as standalone entry, exit or rotation signal.
- Do not change Master Monday, RAW, Cycle Navigator or DATA PING architecture.
- Do not promote any proxy before causal walk-forward tests and baseline comparison.

## 4. Candidate proxy families

### SMB-A — Cohort Cost Basis Envelope
Inputs:
- Realized Price
- STH and LTH realized price
- cohort realized prices by holding age
- URPD-style acquisition-price distribution

Hypothesis:
SMB is primarily a reliability-weighted envelope around economically important cost bases.

### SMB-B — Lifespan Pressure Envelope
Inputs:
- Spent Output Age Bands
- Coin Days Destroyed / dormancy
- revived supply by age
- UTXO survival or hazard weighting

Hypothesis:
Structural zones reflect the price levels where increasingly mature capital is likely to become active.

### SMB-C — Multi-Horizon Capital Structure
Inputs:
- 30d, 90d and 365d market-cap movement
- realized-cap momentum over the same horizons
- age-weighted realized price
- supply in profit/loss

Hypothesis:
The published description is best approximated by combining lifespan reliability with multi-horizon capital expansion and contraction.

### SMB-D — Minimal Public-Data Proxy
Inputs:
- BTC price
- realized price or closest available public substitute
- long-horizon logarithmic trend
- causal volatility/quantile envelope

Purpose:
Establish whether complex on-chain data adds value over a cheap reproducible baseline.

## 5. Baselines

Every proxy must be compared against:

1. Price-only causal volatility bands
2. Realized Price
3. STH/LTH cost basis where available
4. MVRV-style bands
5. CVDD / Delta Cap where reproducible
6. URPD concentration zones where available
7. Simple rolling quantile bands
8. Horizontal swing support/resistance

## 6. Phased research plan

### Phase 0 — Source and claim freeze
Deliverables:
- source ledger
- exact public claims
- unknowns register
- prohibited inferences

Pass condition:
All claims trace to primary or first-party sources.

### Phase 1 — Data feasibility and provenance
Deliverables:
- data dictionary
- source, cadence, start date and revision risk for each field
- free/public vs licensed availability
- point-in-time availability assessment

Pass condition:
At least one proxy family can be built causally with reproducible data.

### Phase 2 — Mathematical specification
Deliverables:
- explicit formula for SMB-A through SMB-D
- fixed parameters or pre-registered parameter grids
- no future leakage
- band-width and penetration definitions

Pass condition:
Independent implementation is possible from the specification alone.

### Phase 3 — Historical reconstruction
Periods:
- 2013–2015
- 2017–2019
- 2020–2022
- 2023–2026

Deliverables:
- causal daily bands
- regime event table
- breach and reclaim log
- parameter stability report

Pass condition:
No chart-only fitting and no unexplained parameter changes between cycles.

### Phase 4 — Baseline benchmark
Primary metrics:
- support-zone hit rate
- resistance-zone hit rate
- median maximum adverse excursion after first zone contact
- time spent inside zones
- false-zone rate
- breach-to-reclaim probability at 3d, 7d, 14d and 30d
- range-placement error
- incremental information versus each baseline

Pass condition:
A proxy must beat at least two simple baselines on pre-registered metrics in more than one regime.

### Phase 5 — Walk-forward and robustness
Tests:
- expanding-window calibration
- fixed-parameter holdout
- parameter perturbation
- missing-data degradation
- lost-coin and dormant-supply sensitivity
- entity-adjusted versus raw UTXO variants where available

Pass condition:
Utility survives out-of-sample and does not depend on one cycle or narrow parameter choice.

### Phase 6 — Framework relevance test
Candidate uses:
- structural floor context
- downside-depth adjustment
- 5–7d range placement
- Pullback Wave Size context
- Bottom Cluster Validation
- post-flush Vacuum / Mixed / Absorption classification
- Capital Protection context

For each use, measure whether the proxy changes a forecast or action translation and whether that change improves the outcome.

Pass condition:
Documented decision value, not merely visual similarity or explanatory value.

### Phase 7 — Forward shadow test
Minimum:
- 30 daily rows
- preferably 90 days

Fields:
- proxy values and bands
- price position
- penetration percentage
- counter-pressure state
- predicted structural path
- actual 3d/7d/14d outcome
- baseline outcome
- framework impact: NONE / CONTEXT / MATERIAL

Pass condition:
Pre-registered rows show incremental value with acceptable false-positive cost.

### Phase 8 — Governance verdict
Allowed verdicts:
- REJECT
- EXPLANATORY_ONLY
- SHADOW_CONTEXT
- RANGE_OVERLAY_CANDIDATE
- PROMOTION_REVIEW_REQUIRED

Promotion is not automatic even if tests pass.

## 7. Kill criteria at birth

Terminate or freeze the research if any of the following occurs:

1. No causal reproducible proxy can be built from available data.
2. Performance does not exceed simple baselines outside one selected regime.
3. Small parameter changes materially reverse conclusions.
4. The proxy only looks useful on logarithmic full-history charts but fails event-level tests.
5. Data revision or point-in-time limitations make historical results non-auditable.
6. Incremental framework impact is zero or duplicative.
7. The proxy improves explanation but worsens action or range outcomes.

## 8. Initial framework mapping

Potential output only:

```text
STRUCTURAL_BAND_STATE:
Below Support / Inside Support / Neutral Corridor / Inside Resistance / Above Resistance

BAND_PENETRATION:
0–100%

COUNTER_PRESSURE:
Weak / Building / Strong

EVIDENCE_QUALITY:
Low / Medium / High
```

No standalone action follows from these fields.

## 9. Current state

Phase 0: OPEN
Phase 1: OPEN
All later phases: BLOCKED until source and data feasibility are complete.
