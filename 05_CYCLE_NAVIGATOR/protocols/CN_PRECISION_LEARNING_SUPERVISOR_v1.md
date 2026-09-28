# Cycle Navigator Precision Learning Supervisor v1

Status: ACTIVE_INTERNAL_ONLY  
Authority: RESEARCH_ONLY_NON_CANONICAL

## Purpose

Turn the append-only internal Cycle Navigator precision history into compounding calibration learning without changing the established public precision surface used by SITE and X.

The supervisor sits downstream of the weekly internal precision settlement. A single weak week is evidence, not a mandate. Repeated weakness across settled weeks can mature into a bounded research question.

## Two-speed design

1. Weekly deterministic trend monitor
   - reads only settled internal precision ledgers;
   - computes recent four-settlement family statistics, prior-window comparison, weak-week counts, zero-score counts and streaks;
   - preserves missingness and requires scoreable observations;
   - never changes forecasts, thresholds, weights, public scores or portfolio state.

2. Four-settlement deep checkpoint
   - runs after each four new successful internal CN settlements, not every fourth calendar week;
   - compares the latest four settlements with the preceding four and the available history;
   - looks for persistent weakness, repeated error classes and cross-family blind spots;
   - may request a bounded API deep review only when deterministic evidence warrants it.

## Deterministic escalation

The active thresholds live in `05_CYCLE_NAVIGATOR/internal_learning/POLICY.json`.

States:
- NORMAL
- WATCH
- PERSISTENT_WEAKNESS
- DEEP_REVIEW

Research escalation is deterministic. AI analysis cannot create the escalation trigger.

When a four-settlement checkpoint contains persistent weakness, the supervisor exposes a research-only specialist proposal. That proposal is consumed through the existing Research Governance Stack and must pass novelty, decision-impact/VOI, independent adversarial review, meta-orchestration and scientific admission before any prospective experiment can exist.

## Hysteresis

A persistent or deep-review family does not return directly to NORMAL after one good observation. Two latest valid scores must satisfy the recovery floor before the state can fully clear.

## API role

Routine deep checkpoint: Terra medium.  
Severe repeated failure: Sol high.

API output may:
- search for common causes across families;
- identify regime dependence or timing bias;
- distinguish forecast weakness from overly rigid claim wording;
- propose bounded falsifiable shadow hypotheses.

API output may not:
- trigger its own escalation;
- change thresholds, weights, market state, forecast authority or portfolio execution;
- alter historical settlements;
- alter SITE/X public precision semantics;
- create public score fields;
- generate canonical forecast candidates.

## Public firewall

Internal learning is intentionally richer than public communication.

The existing SITE and X precision values are a shared public continuity surface. They are immutable with respect to this supervisor. Internal additions, poor internal scores, new families, checkpoints or API reviews must never delete, replace, recompute or automatically expand the public score model.

A change to public precision requires a separate explicit owner-approved versioned public migration.

## No deletion

This supervisor inherits the additive-only internal precision rule. Existing internal families and historical values remain preserved. New families may be added prospectively. Obsolete families are deprecated with lineage, never erased.

## Governance output

The supervisor state is a specialist input only. It has no canonical or portfolio authority. Its role is to create a better question when several weeks of evidence indicate that the framework may be systematically weak in one area.
