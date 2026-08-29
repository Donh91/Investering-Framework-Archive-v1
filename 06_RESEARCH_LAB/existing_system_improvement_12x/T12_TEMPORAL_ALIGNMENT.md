# T12 - Temporal Alignment / As-of Coherence

**State:** FINDING_FROZEN
**Existing owners:** owner-bound Daily Director context builder; multi-horizon context augmentation

## Current evidence

The context builder correctly freezes a latest supported capture and predecessor, records predecessor age and degrades the delta if the predecessor is older than 48 hours.

The multi-horizon augmentation also correctly records, per horizon:

- target hours;
- anchor timestamp;
- latest timestamp;
- actual span hours;
- sample count;
- unavailable status when no anchor is within an existing tolerance.

This is strong raw timing metadata. Recent Director evidence has nevertheless had nominal horizons whose `actual_span_hours` were materially shorter than their labels, and additional owner families such as settled ETF, rich breadth, stablecoin liquidity and passive pullback forensics carry independent retrieval/observation timestamps.

## Frozen finding

`TEMPORAL_METADATA_EXISTS_BUT_CROSS_OWNER_ASOF_COHERENCE_IS_NOT_COMPACTLY_EXPOSED`

The problem is not absence of timestamps. It is that downstream interpretation still has to manually reason about whether evidence cited together describes sufficiently overlapping market time.

## Required improvement

Add a deterministic, read-only temporal-coherence block to the existing Director context. It must use existing timestamps/tolerances and expose raw facts rather than inventing new market thresholds:

- decision cutoff timestamp;
- timestamp/age for every included owner family that exposes one;
- max/min observation age and age spread;
- per-horizon target hours versus actual span and anchor lag;
- exact owner families with unavailable/unknown timestamps;
- whether any existing owner-specific freshness/tolerance contract was violated;
- `cross_owner_alignment_status` limited to `WITHIN_EXISTING_CONTRACTS / EXISTING_CONTRACT_VIOLATION / UNKNOWN`, avoiding a new arbitrary skew threshold.

## Interpretation rule

Evidence from materially different as-of times may still be shown, but the Director must not describe their apparent disagreement as simultaneous market conflict without noting temporal mismatch.

No data are interpolated, forward-filled or shifted to force alignment.

## Acceptance

Positive: a fixture with mixed owner timestamps reports exact age spread and the relevant existing-contract violation; a fully valid fixture reports `WITHIN_EXISTING_CONTRACTS`.

Negative: no new freshness threshold is invented; unknown timestamps do not become stale by assumption; no owner data are dropped, interpolated or re-timestamped to make the packet look aligned.
