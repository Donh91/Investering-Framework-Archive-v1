# Weekly Shadow Relevance Calibration v1

Status: RESEARCH_ONLY
Canonical impact: NONE

## Goal

Provide a weekly calibration surface that can compare passive shadow sensors with the canonical framework without allowing shadow outputs to alter live rules, thresholds, weights or portfolio execution.

## Weekly questions

For each registered shadow sensor:

1. Did it fire or materially change this week?
2. Was its source fresh, reproducible and continuous?
3. Did it lead, coincide with or lag materially similar canonical evidence?
4. Did it add information not already present in ETHBTC, breadth, BTC/ETH relative strength, derivatives, liquidity and the Entry Signal Ledger?
5. Did the subsequent outcome support or contradict the shadow interpretation?
6. Was the behavior stable across multiple observations or driven by one episode?
7. Is the sensor useful only in a specific regime?

## Evidence states

Each sensor receives exactly one weekly research state:

- KEEP, useful and still worth observing
- WATCH, insufficient evidence
- REDUNDANT, duplicates existing evidence without useful lead
- NOISE, unstable or high false-positive behavior
- REGIME_SPECIFIC, useful only under a defined context
- UNTESTABLE, provenance/data/definition insufficient
- PROMOTION_CANDIDATE, sufficiently promising to justify a separate prospective forward-test proposal

## Minimum metrics

Where source data support them:

- observation count
- lead/lag versus nearest comparable canonical state change
- false-positive rate
- miss rate
- source freshness failures
- missingness/continuity failures
- outcome direction at +6h, +12h, +24h, +48h, +72h, +7d
- incremental-value note after controlling qualitatively or quantitatively for canonical comparators

Longer-horizon sensors may additionally use +14d and +30d.

## Anti-double-counting rule

Multiple shadows derived from the same underlying input family must not be counted as independent confirmations. Family-level correlation/redundancy must be surfaced explicitly.

## Promotion firewall

`PROMOTION_CANDIDATE` does not alter the framework. It permits only a separate proposal for prospective testing. Historical fit, weekly score or research enthusiasm can never directly modify canonical semantics.

## Master Monday integration target

Master Monday may read a compact weekly summary containing:

- top 3 shadow observations worth continued attention,
- sensors downgraded to REDUNDANT/NOISE,
- unresolved provenance/data-quality blockers,
- new PROMOTION_CANDIDATE proposals, if any.

The weekly summary is advisory research evidence only.
