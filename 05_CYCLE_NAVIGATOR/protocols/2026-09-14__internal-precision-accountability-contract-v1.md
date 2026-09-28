# Cycle Navigator Internal Precision Accountability Contract v1

**Date:** 2026-09-14  
**Status:** ACTIVE_INTERNAL_ACCOUNTABILITY  
**Authority:** INTERNAL_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY

## Purpose

Maintain a richer internal forecast/accountability record than the public Cycle Navigator while preserving the public score as a separate communication surface.

The internal layer must prospectively freeze all scoreable Cycle Navigator claims that actually exist, attach outcomes only after the relevant horizon matures, preserve source lineage, and surface a compact weekly Precision Box after Master Monday / Cycle Navigator publication.

## Weekly order

```text
final completed-week evidence
-> Master Monday
-> public Cycle Navigator evaluation + new public freeze
-> internal precision settlement for all matured claims
-> internal freeze of current scoreable claims
-> compact Precision Box
-> append-only ledgers
-> validation
-> commit
-> durable readback
```

## Public vs internal

- `CYCLE_NAVIGATOR_SCORECARD.json` and public/X copy remain the public accountability surface.
- Internal precision does not rewrite public historical scores.
- Internal precision may expose more dimensions and horizons than the public surface.
- Public and internal scores must never be silently averaged together.
- The established public precision presentation is continuity-locked: adding internal precision dimensions does not add, remove, rename or replace public headline scores.
- Public X/site precision semantics change only through a separate explicit owner-approved public migration.

## Precision permanence — additive-only internal evolution

The internal precision system is **monotonic and additive**.

- Existing score families, settled historical scores, append-only ledger rows and established internal precision dimensions MUST NOT be deleted, silently removed, collapsed, renamed into a different meaning, or replaced merely to simplify the system.
- New precision dimensions MAY be added when they are prospectively frozen, objectively evaluable and source-bound under this contract.
- New dimensions extend the internal accountability surface; they do not overwrite or retroactively redefine older score semantics.
- If an internal metric becomes obsolete, it must be retained with explicit `DEPRECATED`, `N/A` or equivalent versioned status and preserved lineage. Deprecation is allowed; erasure is not.
- A validator or migration that causes an established internal precision family to disappear MUST fail closed unless a separate explicit owner-approved, versioned migration preserves the old history and semantics.
- Historical rows remain immutable. New methodology versions apply prospectively unless a separately documented reproducible migration is explicitly authorized.
- Internal expansion MUST NOT by itself change the public precision presentation on X or the public site.

This rule exists so the internal layer can become richer over time without losing calibration history or moving the scoring goalposts.

## Scoreable families

Where prospectively frozen and objectively evaluable, the internal layer tracks at least:

- weekly structural / regime;
- BTC and ETH weekly ranges;
- ETH/BTC;
- breadth;
- leadership / transmission;
- rotation;
- altseason;
- Day 1-2, Day 3-4 and Day 5-7 intraday maps;
- 2-3 week base case;
- 4-8 week base case;
- additional ratified generic framework forecasts only after their own scientific freeze and settlement gates pass.

`UNAVAILABLE`, null or never-frozen claims are not reconstructed retrospectively. They are shown as N/A/unfrozen and excluded from hit/miss denominators.

## Scoring

For categorical claims:

```text
SUPPORTED      = 100
MIXED          = 50
CONTRADICTED   = 0
NOT_EVALUABLE  = null
```

`NOT_EVALUABLE` means evidence is incomplete or the outcome cannot be established under the frozen contract. Missing data never becomes a miss and never becomes a hit.

Aliases and materially correlated duplicate claims remain individually auditable but are excluded from family headline aggregation. No synthetic overall internal accuracy is published unless a future preregistered aggregation method explicitly handles dependence and weighting.

## Freeze integrity

Every current internal claim must bind to the exact source public forecast freeze and the machine package that existed when the internal claim was materialized.

After freeze, the following are immutable:

- forecast text;
- claim identity;
- family / source parameter;
- horizon and maturity;
- source hashes;
- alias relationship.

Corrections must be append-only/auditable; no hindsight rewrite is permitted.

## Maturity

- Weekly and intraday claims are evaluated only after the target week/window is complete and authoritative completed-period evidence exists.
- 2-3 week and 4-8 week claims remain pending until their frozen maturity week.
- Mature long-horizon claims may use a bounded internal scorer only with the complete sequence of final Master Monday evidence across the frozen horizon.
- If full evidence is unavailable, score `NOT_EVALUABLE` or leave the claim visibly awaiting settlement; never infer the result.

## Coverage invariant

Every mature parameter from the preceding public freeze must appear exactly once in the internal settlement surface.

The weekly validator must fail closed for:

- silent omission of a mature frozen parameter;
- duplicate parameter or claim IDs;
- score/status mismatch;
- source-hash mismatch;
- mutation of current frozen claims;
- alias double-counting in headline family scores;
- missing summary/detail ledgers;
- missing compact Precision Box.

## Compact owner surface

`CYCLE_NAVIGATOR_INTERNAL_PRECISION_BOX.md` is deliberately limited to a few lines. It should show, where available:

```text
Weekly structural | Intraday | mature coverage
Regime | ETH/BTC | Breadth | Leadership
Rotation | Altseason | BTC range | ETH range
D1-2 | D3-4 | D5-7
frozen/pending/N-A counts + generic scientifically-settled count
one concise self-critique
```

The detailed evidence remains in the machine scorecard and append-only parameter ledger.

## Multi-week precision learning

The settled internal precision ledgers feed `CN_PRECISION_LEARNING_SUPERVISOR_v1`.

- Weekly settlement remains the atomic accountability layer.
- A deterministic trend monitor analyzes every successful settlement.
- A deep checkpoint occurs after every four new successful settled CN weeks, not by calendar modulo.
- The checkpoint compares the recent four settlements with the preceding four and preserved history.
- Persistent family weakness may create a research-only hypothesis proposal through the existing Research Governance Stack.
- AI may analyze causes only after a deterministic trigger; AI cannot create its own escalation.
- This learning layer is additive-only and has zero authority over public SITE/X precision values.

## Generic forecast stack boundary

Generic `research/api_agent` forecast candidates are supplementary only. Candidate existence is not a frozen prediction and cannot enter internal hit-rate accounting until the generic stack has passed its own ratification, freeze, maturity, lineage and settlement gates.

The internal CN layer must not weaken those scientific gates merely to increase sample count.

## Authority ceiling

This layer has no authority to:

- change Master Monday;
- change market regime/state;
- change thresholds or model weights;
- promote research rules;
- execute or recommend portfolio actions by itself.

Its role is accountability, calibration and self-critique.
