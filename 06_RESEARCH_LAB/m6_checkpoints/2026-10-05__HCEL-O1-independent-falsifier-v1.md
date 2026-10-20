# M6 HCEL O-1 independent falsification packet v1

Mission: RL-DISTRIBUTION-SURVIVAL-META-006
Subtask: HCEL_O1_INDEPENDENT_CONTINUITY_FALSIFIER
Date: 2026-10-05
Authority: RESEARCH_ONLY

## Claim to falsify

Claude reports that HCEL's original daily engine stitched disconnected 2021 and 2025 rows positionally, materially biasing 54/504 policy-result cells and changing aggregate E1/E3 ranking.

Do not trust Claude's derived continuity engine merely because its diagnosis is plausible.

## Bound evidence

Bridge findings to independently challenge:
- original 504-row hash reproduced exactly;
- panel has two disconnected windows;
- 2025-01-01 boundary index 487;
- positional rolling borrows 2021 rows into early 2025;
- continuity-safe reference changes 54/504 rows;
- affected episodes only EP-03 and CTRL-03;
- E3 EP-03 ETH TWR 1.788 -> 1.205;
- E3 W_A cost20 +0.0096 -> -0.0208;
- W_C winner E3 -> E1 at all costs;
- LOEO first counts E3 5/E1 3 -> E1 6/E3 2.

Paths:
- Bridge/programs/historical_cycle_exit_lab/runs/2026/10/CROSS_WINDOW_TEMPORAL_INTEGRITY_AUDIT.md
- Bridge/programs/historical_cycle_exit_lab/runs/2026/10/evidence/o1_boundary_trace.json
- Bridge/programs/historical_cycle_exit_lab/runs/2026/10/evidence/o1_loeo_ranking.json
- Bridge/programs/historical_cycle_exit_lab/runs/2026/09/POLICY_SPEC_v0.json
- Bridge/programs/historical_cycle_exit_lab/runs/2026/09/evidence/exit_policy_lab.py

## Independent reasoning task

Use an implementation conceptually independent from Claude's loop code.

Prefer:
- group by research_window_id / continuity segment;
- compute rolling features within group;
- derive theoretical warm-up boundaries directly;
- compare which original v0 features are mathematically impossible at early 2025.

You do not need to rerun all market data if the deterministic boundary proof is sufficient, but explicitly distinguish:
- proven structural contamination;
- independently reproduced numeric policy cells;
- numeric cells accepted only from Claude;
- remaining UNKNOWN.

## Spec adjudication challenge

Evaluate proposed POLICY_SPEC_v0_1 R1-R8.

Important challenge from ChatGPT:
- R4's "3 days" external max source age is a NEW parameter, not logically required by v0 repair.
- R6's "5 daily frames" hard-exit grace is a NEW parameter, not logically required by v0 repair.

Assess whether these belong:
A. minimal v0.1 scientific repair;
B. separately preregistered prospective v0.2/safety spec;
C. reject.

Also challenge R5 for whether it changes policy behavior beyond the original missing-data contract.

## Required return

- CONTAMINATION_VERDICT
- STRUCTURAL_PROOF
- NUMERIC_DELTA_CONFIDENCE
- E1_E3_RANKING_STATUS
- R1_TO_R8_DISPOSITION
- MINIMAL_REPAIR_SPEC
- WHAT_MUST_NOT_BE_RERUN_UNTIL_FROZEN
- selected_live_rules=[]

No signal invention.
No market threshold tuning.
No portfolio action.
No repository write.
