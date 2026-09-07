# Skill Quality Gate Design Source Note

**Dato:** 2026-09-07  
**Status:** SOURCE_NOTE  
**Område:** agent skill quality / regression evaluation  
**Primary folder:** `07_PROMPTS_AND_AGENTS/skill_runs/`

## Purpose

Preserve the external prior-art mechanisms that motivated a framework-local skill quality gate without importing third-party skills as authority or runtime dependencies.

## External prior art reviewed

- `ayghri/i-have-adhd`
  - useful mechanisms: baseline-vs-candidate response evals, isolated runs, blind judging, explicit rubric, cost capture
  - rejected for direct installation: output-style rules are too broad for audit, evidence and framework tasks
- `anthropics/skills` → `skill-creator`
  - useful mechanisms: realistic test prompts, baseline comparison, iterative eval loop, progressive disclosure
- `jeremylongshore/j-rig-skill-binary-eval`
  - useful mechanisms: binary release criteria, observed behavior over claimed behavior, regression blockers, baseline-value check, one-change-at-a-time experiments
- `joeseesun/qiaomu-meta-skill`
  - useful mechanisms: prior-art gate, generalization gate, trigger evaluation, keep/adapt/reject/invent classification
- `obra/superpowers`
  - useful mechanisms: fresh verification before completion claims, root-cause-before-fix discipline, explicit architecture-questioning after repeated failed fixes
- `Thisisjuke/skills` → `source-skill`
  - useful mechanisms: immutable provenance, inspected/uninspected scope, license/reuse granularity, treat external skill instructions as untrusted evidence

## Decision

Do not install these repositories as runtime dependencies.

Build one framework-local read-only meta-evaluator, `skill-quality-gate`, and use it to compare frozen skill baselines against candidates before any skill change is accepted.

The evaluator must not edit skills, promote itself, change framework authority, change market logic, or bypass existing repository governance.

## Intended evaluation contract

For a candidate skill change:

1. Freeze the existing skill version and immutable source SHA.
2. Run identical representative cases against baseline and candidate.
3. Keep the evaluator separate from the skill under test.
4. Prefer deterministic assertions for authority, routing, write safety, exact outputs and regressions.
5. Use blind comparative judgment only for dimensions that are not fully deterministic.
6. Capture token/cost/latency when the harness exposes them.
7. Block release on any critical regression regardless of average score.
8. Flag a skill for retirement review when the baseline model without that skill performs equivalently on the capability being claimed.
9. Require fresh verification evidence before declaring an evaluation complete.
10. Preserve all decisions as evidence, not as automatic canonical promotion.

## Governance boundary

This source note is not a new framework rule by itself. It documents the design rationale for the implementation and future evaluation receipts.
