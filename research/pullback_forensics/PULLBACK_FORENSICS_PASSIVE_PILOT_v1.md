# Pullback Forensics Passive Pilot v1

**Status:** RATIFIED — PASSIVE SHADOW RESEARCH ONLY  
**Ratified:** 2026-08-12  
**Execution class:** `PASSIVE_EVIDENCE_CAPTURE`  
**Canonical authority:** NONE  
**Portfolio authority:** NONE

## Purpose

Preserve perishable evidence that the existing hourly sequence and live-anchor stack cannot reliably reconstruct later, so pullback / flush / failed-recovery learning can be tested prospectively once the baseline has matured.

This pilot does **not** assert incremental predictive value. At ratification time the hourly baseline was too young for a statistically defensible incremental-value test. Capture is authorized because selected source data are perishable, not because a trading edge has been proven.

## Frozen lane decisions

- **L1 Executed liquidations — START.** OKX exact BTC-USDT-SWAP and ETH-USDT-SWAP only. Preserve raw event fields, contract metadata and deduplicated event identity. All aggregate values remain lower-bound research observations while endpoint page completeness is unverified.
- **L2b Options moneyness skew — START as rider.** Deribit exchange-native current option chain. Store per-expiry days-to-expiry and moneyness-bucket skew. This is explicitly **NOT 25-delta skew**.
- **L4 Catalyst/confound attribution — START prospectively in Claude OTA.** Classification timestamp must precede the frozen outcome-window end. Historical back-tagging is not evidence.
- **L2a DVOL — DEFER.** Backfillable later; no information is permanently lost by waiting.
- **L3 Order-book dynamics — DEFER.** Five-times-daily / OTA cadence cannot measure minute-scale depth evaporation, refill or cancellation dynamics.

## L1 unit-semantic correction

OKX liquidation `sz` is treated as **contracts**, not BTC/ETH units. For the exact linear USDT perpetual instruments used by this pilot, USD notional is normalized from contract count, `ctVal`, and bankruptcy price. `ctMult` is retained as source metadata and the collector fails closed if it is not `1`, requiring a versioned semantic review instead of silently extending the formula.

The earlier external-research illustration that multiplied `sz × bkPx` is therefore not admissible evidence and is not imported.

## Source fragility

The OKX liquidation REST surface is treated as `LEGACY_REST_STILL_LIVE_SOURCE_FRAGILE`. A source failure produces `UNKNOWN`; it is never interpreted as zero liquidations or market evidence.

The collector stores normalized raw event rows with source-payload hash and contract metadata so future feature definitions can be recomputed from captured evidence.

## Cadence and failure isolation

The pilot reuses the existing **five-times-daily Daily Live Anchor Capture** workflow. It creates no new schedule, workflow, OpenAI spend or CFGI spend.

The live anchor is committed before Pullback Forensics. Pullback Forensics runs `continue-on-error` and commits independently. A forensic-source failure therefore cannot invalidate the ordinary live anchor or the blinded prospective evidence lane.

## Research topology

`RESEARCH_EXECUTION_TOPOLOGY_v1` preserves exactly one global `EXPERIMENT_EXECUTION` slot. The Deep Research Horizon Queue remains `RESEARCH_CONTEXT` only, and this pilot is passive evidence capture. Neither consumes the global experimental execution slot.

## Provenance

External research packages independently verified by SHA-256 before ratification:

- `PULLBACK FORENSICS RESEARCH RESULTS v1.zip` — `9e020c997253f18cb0dee6dd9f0a31c2d08ac487067fa1ea2570768594706f9c`
- `RESEARCH THREAD STATUS 20260811.zip` — `23f0ea05e521d61fa1f3bbeb478102b1367f08dd8c24e0fa5c0cc4a3f225170c`

## Hard boundary

No captured field may alter market state, gates, thresholds, weights, entry/rebuy/trim permission or portfolio action without a separate prospective evidence review and explicit governance ratification.
