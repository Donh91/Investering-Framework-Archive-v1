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

## Owner schema and evaluator binding

The runtime loads the existing owner schema at `06_RESEARCH_LAB/historical_sensor_recovery_v1/SHADOW_SENSOR_REGISTRY_SCHEMA.json`. Required fields, owner enums and the authority firewall are enforced instead of maintaining a reduced parallel schema.

`SCORABLE` is not inferred from an evaluator-looking string or an existing folder. The current registered Entry Signal evaluator must bind to its producer and exact output bytes, use the registered complete horizon set, and pass count/mean consistency checks. Placeholder breadth labels and research-artifact labels remain `RECOVERY_REQUIRED` until an explicit evaluator contract exists.

Output-shape validation does not certify fixed-horizon accuracy, source independence, sample independence or economic value. Those remain separate scientific questions.

## Calibration readiness

- `SCORABLE` - a registered evaluator exists and its current output passes the bound output-contract checks.
- `RECOVERY_REQUIRED` - source material exists but exact historical semantics/evaluator still need recovery.
- `SOURCE_MISSING` - one or more registered evidence paths are absent.

These states are about research readiness, not market direction.

## Weekly immutability

The first valid `weekly/YYYY-Www.json` for a week is immutable. Same-week reruns preserve that file byte-for-byte and may refresh only `LATEST.json`. A malformed existing weekly snapshot is preserved and causes an explicit failure instead of being silently replaced. New weekly writes are installed atomically to avoid leaving truncated evidence after an interrupted write.

Historical pre-remediation weekly files are not silently rewritten or retrospectively recertified by the stricter runtime.

## Reviewed publication lane

Shadow Registry artifacts are registry/governance-lane material under the Continuity + Learning architecture. The scheduled workflow therefore does not push generated registry artifacts directly to `main`.

Each weekly run writes to a deterministic `automation/shadow-registry-YYYY-Www` branch and opens or reuses a pull request. Normal repository CI/review is required before the generated evidence can reach `main`. The scheduler has no authority to bypass that review boundary.

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
