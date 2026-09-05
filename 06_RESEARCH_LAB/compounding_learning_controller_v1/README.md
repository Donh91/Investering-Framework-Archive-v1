# Compounding Learning Controller v1 — Astra Handoff

**Status:** `HOLD_FOR_ASTRA_REVIEW`  
**Authority:** `RESEARCH_ONLY_NON_CANONICAL`  
**Prepared:** 2026-09-05  
**Purpose:** preserve the design, audit findings, implementation intent and acceptance criteria for a future Astra-led build/review.

## Why this exists

The framework already has the correct experimental evidence machinery:

- Experiment Lifecycle & Execution Plane;
- Scientific Admission;
- Unified Experimental Lifecycle Adjudication;
- prospective frozen forecasts and outcome maturation;
- immutable research receipts and authority boundaries.

The missing layer is **not another experiment engine**.

The missing layer is a controller that operates *after* mature evidence and adjudication and answers:

1. What did the framework actually learn?
2. What remains uncertain?
3. What assumption was strengthened, weakened or falsified?
4. What is the highest-value next prospective test?
5. What should be deliberately left unchanged?

This is the intended compounding loop:

`FROZEN ASSUMPTION -> PROSPECTIVE TEST -> OUTCOME -> ADJUDICATION -> LEARNING SYNTHESIS -> NEXT BEST TEST`

## Non-negotiable architecture boundary

The Compounding Learning Controller must **not** replace or duplicate Unified Experimental Adjudication.

- **Unified Adjudication owns:** evidence interpretation and lifecycle action from existing mature experiment evidence.
- **Compounding Learning Controller owns:** synthesis across mature/adjudicated results and selection of the next best *research question/test proposal*.

The controller may propose. It may not silently promote.

## Current implementation artifact

An earlier exploratory branch exists:

`agent/task-20260904-compounding-learning-v1`

It contains a first controller implementation commit:

`fe00da2efe78a5f4b5666b3edba636d09e34edd4`

That branch was intentionally **not merged** because it diverged from newer main architecture and was behind current main. Treat it as a design/code salvage source only.

Do not merge or rebase it blindly.

## Astra instruction

When Astra is available, begin with:

1. read this folder completely;
2. read current `main` before touching the old branch;
3. audit current Experiment Lifecycle, Scientific Admission and Unified Adjudication contracts;
4. compare the exploratory controller branch against current main;
5. salvage only compatible logic;
6. redesign/rebuild on a fresh task branch from then-current main;
7. run adversarial architecture and scientific-governance review before merge.

## Required discovery paths

Astra should inspect at minimum:

- `00_FMOS/EXPERIMENT_LIFECYCLE_AND_EXECUTION_PLANE_v1.md`
- `00_FMOS/EXPERIMENT_SCIENTIFIC_ADMISSION_AND_UNIFIED_ADJUDICATION_v1.md`
- `scripts/experiments/unified_experimental_adjudication.py`
- `.github/workflows/unified-experimental-lifecycle-adjudication.yml`
- `.github/workflows/framework-learning-operations.yml`
- `research/experiment_lifecycle/`
- `research/framework_memory/`
- `06_RESEARCH_LAB/protocols/`
- this folder

## Hard guardrails

The final implementation must preserve all of these:

- no retrospective fabrication of prospective evidence;
- no automatic canonical promotion;
- no automatic market-rule, threshold or weight change;
- no portfolio execution authority;
- no overwrite of frozen forecasts, admissions, outcomes or prior adjudications;
- no self-validating experiment loop;
- no reward for merely increasing the number of experiments;
- no outcome peeking when proposing prospective tests;
- explicit complexity tax and redundancy checks;
- deterministic, auditable outputs;
- append-only or versioned learning history;
- full compatibility with repository safety and destructive-authority separation.

## Stop condition

Until Astra review is explicitly started, this folder is documentation only.

**Do not activate a new workflow, merge the exploratory controller branch, or grant the controller runtime authority.**
