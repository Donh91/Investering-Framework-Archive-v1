# Cycle Navigator Internal Precision

**Contract:** `CN_INTERNAL_PRECISION_v1`  
**Authority:** accountability and learning only; no portfolio execution, framework-state change, model-weight change or public track-record rewrite.

## Purpose

The public Cycle Navigator score is a compact public-accountability surface. The internal precision layer is the richer weekly audit surface behind it.

Every Monday after final Master Monday and Cycle Navigator generation, the internal layer must:

1. preserve the public score separately;
2. expose every scoreable frozen parameter individually;
3. group those rows into compact families (weekly, regime, ETH/BTC, breadth, rotation, altseason, BTC/ETH ranges and intraday Day 1–2 / Day 3–4 / Day 5–7);
4. preserve misses and self-critique rather than averaging them away;
5. bind the evaluation to final Master Monday and the exact CN scorecard by SHA-256;
6. freeze the next issue's internal forecast inventory prospectively;
7. retain longer-horizon scenario forecasts as pending rather than scoring them before maturity;
8. never reconstruct a missing historical forecast after outcomes are known.

## Activation boundary

The richer prospective internal forecast set activates with **CN #27**. CN #26/W38 predates this layer. Its existing public W38 freeze remains authoritative and must not receive retrospectively invented intraday calls. W37 evaluation may be imported only from already-frozen CN #25 evidence and the existing exhaustive W37 parameter-coverage audit.

## Scoring semantics

For categorical CN parameters, reuse the frozen public contract:

- `SUPPORTED = 100`
- `MIXED = 50`
- `CONTRADICTED = 0`
- `NOT_EVALUABLE = null`

`missing != miss`. Null/unpublished ranges are not forecasts and cannot receive either hit or miss credit.

Family scores are transparent unweighted means of mature/evaluable parameter rows within that family. They are internal diagnostics, not a replacement for the official public structural score.

## Immutability

Prospective forecast sets are write-once. A second write with identical bytes is a no-op; any drift fails closed with `IMMUTABLE_ARTIFACT_DRIFT`.

Evaluation artifacts are also write-once. A later evidence correction requires an explicit audited correction path rather than silent overwrite.

## Compact internal CN

`CYCLE_NAVIGATOR_INTERNAL.md` is the owner-facing weekly CN. It starts with an eight-line maximum Precision Box, then includes the full readable CN. Machine detail remains in `CYCLE_NAVIGATOR_INTERNAL_PRECISION.json` and the cumulative internal ledger.

The public/X-ready CN remains separate and unchanged by this layer.
