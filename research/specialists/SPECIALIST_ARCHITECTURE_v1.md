# SPECIALIST INTELLIGENCE LAYER v1

Status: SHADOW-ONLY ARCHITECTURE

## Purpose

Create a set of narrow research specialists that read verified owner-data and produce comparable, auditable observations for DATA PING, RAW, Forecast Ledger and Master Monday.

The layer does not create a second truth system.

## Authority hierarchy

1. Owner-source rows and receipts
2. DATA PING truth layer
3. Specialist observations
4. Specialist Director synthesis
5. RAW and Master Monday interpretation
6. Chief execution layer

A lower layer may not rewrite a higher layer.

## Specialists

### Macro Specialist
Inputs: FRED macro core, liquidity state, rates, dollar and volatility.
Output: macro pressure, direction, persistence, freshness and uncertainty.

### Spot Structure Specialist
Inputs: BTCUSDT, ETHUSDT and direct ETHBTC settled owner rows.
Output: trend, range placement, acceptance, failed persistence and relative leadership.

### Derivatives Specialist
Inputs: venue-specific funding, open interest and mark price. OKX and future venues remain separate owners.
Output: leverage pressure, crowding, deleveraging and venue disagreement.

### Breadth Specialist
Inputs: point-in-time Top-100 constituents, exclusions and membership hash.
Output: participation, displacement, survival and membership-parity status.

### Cycle Specialist
Inputs: canonical Forecast Ledger, Cycle Navigator, TechDev reference and archived cycle rules.
Output: cycle context, hypothesis alignment and explicit reference-vs-owner separation.

## Shared output contract

Each specialist must emit:

- specialist_id
- run_id
- as_of_utc
- owner_inputs
- owner_receipts
- freshness_status
- state
- direction
- confidence_0_100
- persistence_status
- evidence_for
- evidence_against
- missing_required_inputs
- conflicts
- no_action_reason
- authority flags

## Director rules

The Director:

- validates specialist schemas;
- rejects stale or ownerless claims;
- preserves disagreement;
- computes coverage, not market truth;
- emits a shadow synthesis;
- links synthesis to source specialist run IDs;
- never converts UNKNOWN to neutral;
- never lets specialist count create pseudo-confirmation;
- never changes framework state or portfolio action.

## Anti-overlap rule

Specialists must not duplicate the same causal evidence under different labels. The Director groups evidence by causal family:

- macro liquidity
- spot structure
- relative transmission
- leverage
- breadth
- cycle context

Multiple observations from one causal family count as one family for convergence.

## Learning path

Specialist outputs may later be evaluated through Forecast Ledger and weekly calibration. Promotion requires rows, outcomes, sufficient history and existing governance gates. No specialist receives predictive weight at birth.
