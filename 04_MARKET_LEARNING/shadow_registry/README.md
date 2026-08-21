# Shadow Sensor Registry Runtime v1

Authority: RESEARCH_ONLY / NON_CANONICAL
Portfolio execution: FORBIDDEN
Automatic rule, threshold or weight changes: FORBIDDEN

## Purpose

This runtime keeps recovered and active shadow research visible over time without granting it decision authority. It reuses existing repository evidence, especially the Entry Signal Ledger, historical forward tests, breadth-forward material, Cycle Navigator research, Fable/OTA shadow research and Historical Altseason Pullback Laboratory.

The runtime is intentionally conservative. A weekly pass may verify evidence presence, provenance recency and registered evaluator outputs. It may not infer that a sensor is useful merely because files exist.

## Files

- `REGISTRY.json` - registered sensor/research families and their current research state.
- `LATEST.json` - most recent machine-readable weekly calibration snapshot.
- `weekly/YYYY-Www.json` - immutable weekly snapshots by ISO week.

## Calibration readiness

- `SCORABLE` - a pre-registered evaluator exists and its evidence is available.
- `RECOVERY_REQUIRED` - source material exists but exact historical semantics/evaluator still need recovery.
- `SOURCE_MISSING` - one or more registered evidence paths are absent.

These states are about research readiness, not market direction.

## Weekly relevance states

The registry can ultimately carry `KEEP`, `WATCH`, `REDUNDANT`, `NOISE`, `REGIME_SPECIFIC`, `UNTESTABLE` or `PROMOTION_CANDIDATE`.

The weekly runtime does not automatically promote or demote a sensor from simple file presence. Source-specific evaluators, sufficient outcome rows and anti-redundancy analysis are required.

## Promotion firewall

`PROMOTION_CANDIDATE` can only trigger a separate prospective forward-test proposal. Historical fit and weekly shadow performance cannot modify canonical market semantics.

## Relationship to Master Monday

The weekly snapshot is designed to be read as advisory research context by the weekly framework review. It can surface:

- newly matured shadow evidence,
- recovery gaps,
- source-quality problems,
- redundant families,
- candidates deserving continued observation.

It must remain separate from canonical market-state computation.
