# M6 Deterministic Evidence Checkpoint v2

**Mission:** `RL-DISTRIBUTION-SURVIVAL-META-006`  
**Date:** 2026-10-05  
**Status:** SOL_READY_BOUNDED_TRIAGE  
**Authority:** RESEARCH_ONLY  
**Framework main:** `4c4ba555867f5514fd8641693cbf763e7067da1e`

## Delta since v1

1. T4's missing scheduled 7D row has been reconstructed for research only from Binance public BTCUSDT 1m data.
2. The reconstruction reproduces the historical canonical 24h and 72h high/low/close values exactly to USD 0.00 delta.
3. The 7D result materially strengthens the warning-not-sell falsification case.
4. Claude slice 1 independently identified a segment-local `ew_index` rebasing hazard and very low independent terminal-distribution sample size.
5. A primary episode-family clustering rule is now frozen before Sol adjudication.

## T4 7D research reconstruction

Artifact:
`06_RESEARCH_LAB/m6_replay/2026-10-05__PULLBACK_EDGE_20260708_01__7d-reconstruction-v1.json`

Historical warning anchor:
- 2026-07-08T14:03:00Z
- BTC 61,784.48

Canonical positive controls:
- 24h high/low/close reproduced exactly
- 72h high/low/close reproduced exactly

7D research reconstruction:
- low 61,544.56
- high 65,577.00
- close 65,171.99
- max additional downside -0.3883%
- max favorable excursion +6.1383%
- terminal return +5.4828%

Interpretation boundary:
- not an original July maturation row;
- not historical ledger rewrite;
- admissible M6 research reconstruction because the data method exactly reproduces both previously persisted maturity horizons;
- no sell rule follows from a single event.

Economic falsification significance:
An immediate trim at the explicit T4 warning would have avoided at most 0.388% additional BTC downside in this 7D window while surrendering up to 6.138% favorable excursion if not re-entered promptly.

This is strong evidence that:
`WARNING != AUTOMATIC_SELL`.

## Claude slice 1 accepted research deltas

Blind Claude slice:
`AUDIT-20261005-095620Z-CLAUDE-RL010-CENSUS-POWER-SLICE`

Accepted deltas:
- `ew_index` is segment-local and rebases near 100 at continuity boundaries.
- Future M6 tape replay must chain `ew_return_1h_pct` within continuity segments.
- Cross-gap paths must be gap-tagged and never treated as continuously observed.
- historical price-only lane contains few genuinely independent terminal/cycle-scale episode families.
- existing tape-only price/volume/taker-share mining has not beaten HOLD under the prior terminal lab decision.
- historical-as-was overlap remains unproven and is being tested separately by Claude slice 2.

Do not use Claude agreement as independent evidence of economic edge.

## Frozen independent episode-family rule

Primary rule frozen before this Sol pass:

1. Generate candidate peak-to-trough episodes separately at each preregistered drawdown sensitivity threshold.
2. Sort candidates by peak time.
3. Two candidates are the same independent family if:
   - their peak-to-trough windows overlap; OR
   - the later candidate peak occurs less than 14 calendar days after the prior candidate trough.
4. Otherwise start a new family.
5. Nested threshold hits within one family do not increase independent N.
6. Drawdown size alone never earns the label terminal distribution or cycle top.
7. Any family crossing an unobserved continuity gap is tagged `GAP_CROSSED`.
8. Report counts both including gap-reconstructed paths and fully observed no-gap paths.

Sensitivity reporting only:
- 7-day separation
- 30-day separation

Do not select whichever gives the strongest result.

## Current evidence-owner state

- SPAR base replay: fresh and successful, descriptive only.
- SPAR fragility: methods-blocked, no placebo/regime freeze.
- T4: one explicit historical pullback warning; 24h/72h historical maturity + validated research-only 7D reconstruction.
- T5 FNP: evaluator/outcome population not ready.
- T6: 15 prospective natural observations, zero eligible first cross, healthy right-censoring.
- Action Compass typed exit-warning calibration: 0 eligible typed rows, prospectively collecting.
- ETF absorption/transmission: blocked behind SPAR fragility / adapter gate.
- historical-as-was Aug-Oct overlap: Claude slice 2 pending blind.

## Questions for GPT-6.1 Sol

Do not invent signals.

Adjudicate only the evidence above and the bound context files.

1. Does M6 deserve continued research, or should it be killed now?
2. Does any evidence support a live sell/trim rule now?
3. How strongly does T4 falsify warning-as-sell?
4. Is staged trim still scientifically worth testing after T4, and if so why?
5. What is the minimum outcome vector required for a staged trim frontier?
6. Is SPAR's current evidence useful enough to justify a new prospective inferential identity, or should M6 wait for Action Compass/T6 natural events instead?
7. Is the frozen episode-family rule defensible for power accounting?
8. What would be the cheapest decisive falsifier from existing owners?
9. What must remain UNKNOWN?
10. Should any framework authority, threshold, market state or portfolio action change now?

Required hard fields:
- `VERDICT`
- `CONTINUE_RESEARCH`
- `LIVE_EXIT_RULE_SUPPORTED`
- `T4_FALSE_EXIT_IMPLICATION`
- `MINIMUM_DECISION_FRONTIER`
- `SPAR_NEXT_STEP`
- `EPISODE_FAMILY_RULE_ASSESSMENT`
- `CHEAPEST_DECISIVE_FALSIFIER`
- `UNKNOWN_LIST`
- `selected_live_rules`

Hard boundary:
`selected_live_rules=[]`

No code write.
No repository authority.
No threshold change.
No portfolio action.
