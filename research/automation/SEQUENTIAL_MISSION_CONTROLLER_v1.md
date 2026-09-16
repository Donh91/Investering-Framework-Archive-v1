# Sequential Mission Controller v1

## Purpose
Provide a small, fail-closed GitHub-native controller for bounded multi-stage engineering missions. It is a sequencing contract, not a parallel research operating system and not a ChatGPT app automation.

## Owner integration
The permanent Framework Supervisor / Codex queue is the execution owner. `SEQUENTIAL_MISSION_CONTROLLER_v1.json` is machine-readable state. The durable GitHub issue is the human-readable journal and evidence ledger.

## State transition
For the active stage only:

1. Read fresh `main`, owner issue, current PR/review state and controller state.
2. Search/reproduce before implementation. If newer `main` already solves the lane, prove it and terminate `CLEAN_NOOP`.
3. Otherwise implement the smallest bounded correction on a branch/PR.
4. Run required CI and negative regressions.
5. Request independent review. The authoring agent/run must not self-verify or self-merge.
6. Any P1/P2 finding, failed check, head drift, authority ambiguity or evidence ambiguity blocks advancement and returns the same stage to correction.
7. Independent verifier must bind approval to the exact head SHA.
8. Merge only with expected-head SHA protection.
9. Read back the merged state from fresh `main`, including the relevant negative/fail-closed behavior.
10. Record exact PR, merged SHA, tests and readback in the owner issue.
11. Only then advance `current_stage` to the next stage.

Never run two stages in parallel.

## Connection Repair #1047 bootstrap
Stage 2 is `CORRECTION_REQUIRED`, not merge-ready. PR #1046 head `f812d1b60ea1c0c4d73cb6ac08a282ec9d561bcc` has three blocking review findings that must be closed with regressions before independent verification:

- orphan matured outcomes without a matching valid frozen forecast must not enter the ledger or cohort state;
- schema-incomplete `FROZEN_FORECAST_v1` records must not count as cohort members;
- supplied forecast/outcome roots must be validated against the declared population, with mismatch failing closed.

After correction, re-run all required checks, obtain independent exact-head verification, merge with expected-head SHA, and perform fresh-main readback. Only then set Stage 2 `DONE` and release Stage 3.

Stages 3-6 retain the exact scope and guardrails of issue #1047. Stage 6 may end `WAITING_FOR_NATURAL_OBSERVATION`; this is a valid terminal state for the engineering sequence and must not be bypassed by synthetic evidence.

## User-intervention policy
Normal progression requires no user prompt between stages. Stop only when the repository itself cannot safely resolve a stop state within existing authority. Do not create a ChatGPT app automation for this mission.
