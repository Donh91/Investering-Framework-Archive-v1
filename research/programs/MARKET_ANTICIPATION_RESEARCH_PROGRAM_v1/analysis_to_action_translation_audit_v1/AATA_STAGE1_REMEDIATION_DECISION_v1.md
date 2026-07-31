# AATA Stage 1 Remediation Decision v1

**Date:** 2026-07-31  
**Status:** REMEDIATION_REQUIRED / STAGE_2_BLOCKED  
**Trigger:** Claude Opus 5 blind audit `AATA_CLAUDE_STAGE1_v1`  
**Accepted aggregate verdict:** `DATA_BLOCKED`

## Decision

Claude's aggregate verdict is accepted.

The initial Stage 1 package passed byte integrity and internal schema checks, but it did not permit the independent source reconstruction that Stage 1 was designed to test. The package also contained a W30 owner-outcome block while declaring itself outcome-free.

This is a packaging and method-contract failure, not evidence that the four AATA source rows were transcribed incorrectly. Claude found zero transcription errors and no authority breach.

## What remains valid

- The non-blended separation of analysis, price translation, action policy, timing and utility remains useful.
- W28 and W29 remain blocked from economic evidence.
- W30 remains imported owner context only and must not be retroactively rescored.
- W31 remains prospectively frozen and unscored.
- No framework, market, rotation, entry, rebuy or portfolio state changes.

## Binding corrections

### 1. Replace the all-weeks blind package

Stage 1 will be rerun as four target-week-isolated units.

Each unit receives only the primary documents that existed for that target forecast week. A later Master Monday may contain the prior week's score, but it may not be used as a source for auditing that prior week.

### 2. Separate extraction from parity

Stage 1B receives primary source documents, schema and methodology only.

`SOURCE_ROWS_W28_W31_v1.json` and all expected decompositions are withheld.

After Claude freezes and hashes its independent extraction, Stage 1C reveals the corresponding expected source row and performs parity comparison. The Stage 1B extraction may not be silently rewritten after the reveal.

### 3. Preserve mixed forecast-and-score artifacts without rewriting history

The archive is not retroactively split for W28-W31. Instead, blind packaging is target-week isolated.

From W32 forward, scoring and new forecast capture should be separately addressable even when published in one weekly report. The AATA research capture must retain explicit source spans for each block.

### 4. Freeze leadership before future outcome joins

No universal historical definition is imposed on W28-W31.

For W32 forward, every leadership call must freeze:

- dimension: relative strength, absolute performance or rotation;
- asset comparison;
- owner metric;
- observation window;
- settlement convention;
- threshold or dead-band;
- confirmation mode;
- dependency cluster.

A leadership result is `BLOCKED` when these fields are absent. The earlier W30 owner label `MISS` remains owner context and is not reopened under the new definition.

### 5. Freeze the action benchmark before future outcomes

The primary action-policy counterfactual is `FIRST_VALID_PERMISSION`, resolved only by the existing permission owner.

The null benchmark is `SOURCE_ANALYSIS_WITH_NO_ACTION`.

`WAIT` is not counted as a separate benchmark when it is identical to the frozen framework action. `NEUTRAL` is forbidden unless a valid benchmark exists and the measured difference falls inside a preregistered dead-band. Otherwise the action result is `BLOCKED`.

### 6. Control dependency inflation

Multiple labels resolved by the same underlying observation belong to one dependency cluster. For W31, ETH/BTC-linked leadership, rotation, continuation and bull-path observations form an `ETHBTC_DEPENDENCY_CLUSTER` and may count at most once toward material-decision-divergence requirements.

### 7. Add an interim kill review

A mandatory review occurs after six temporally valid prospective rows.

The program is killed or retained as descriptive-only when it has produced no independently reproducible decision divergence, no measurable incremental value over existing owners, or more than 25 percent irreducible ambiguity.

## Stage gates

```yaml
stage_1A_integrity: PASS
stage_1B_independent_reconstruction: REISSUE_REQUIRED
stage_1C_source_parity: REISSUE_REQUIRED
stage_1D_method_red_team: PASS_WITH_CORRECTIONS
stage_2_analysis_accuracy: BLOCKED
stage_3_price_translation: BLOCKED
stage_4_action_and_timing: BLOCKED
stage_5_reconciliation: BLOCKED
W31_scored: false
new_economic_scores: 0
final_holdout: SEALED
```

## Authority boundary

```text
NEW ACTIVE TEST: NO
NEW ENGINE: NO
NEW SCORE: NO
CANONICAL TEMPLATE CHANGE: NO
MARKET STATE CHANGE: NO
ROTATION CHANGE: NO
ENTRY CHANGE: NO
REBUY CHANGE: NO
PORTFOLIO ACTION: NO
```
