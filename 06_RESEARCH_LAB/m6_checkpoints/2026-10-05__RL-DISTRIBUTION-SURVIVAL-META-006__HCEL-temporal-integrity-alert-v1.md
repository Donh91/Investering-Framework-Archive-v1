# M6 HCEL Temporal Integrity Alert v1

**Mission:** `RL-DISTRIBUTION-SURVIVAL-META-006`  
**Date:** 2026-10-05  
**Status:** TEMPORAL_REVALIDATION_REQUIRED  
**Authority:** RESEARCH_ONLY  
**Framework main at alert:** `cbc1465cbcb2840dd0d1a21204222b71080ead23`

## Decision

Historical Cycle & Exit Lab remains the correct owner for M6 policy-family research.

However, its Sep-27 historical E0-E6 ranking is temporarily downgraded pending HCEL O-1 continuity-safe reproduction.

Do not promote or quote E3's historical ranking as clean evidence until O-1 adjudication.

## Verified defect

Bridge code:
`programs/historical_cycle_exit_lab/runs/2026/09/evidence/exit_policy_lab.py`

loads the historical panel's disconnected windows into a single positional daily list.

Known panel windows:
- 2020-09-01 -> 2021-12-31
- 2025-01-01 -> 2026-07-31

No observations exist for 2022-2024 in the panel.

The engine stores `research_window_id` as `window`, but rolling feature functions do not use that field or calendar continuity.

Potentially contaminated early-2025 features include:
- SMA20
- SMA50
- SMA140
- rolling high 30/60/90
- drawdown90
- breadth7
- ETHBTC30
- FNG14max
- stablecoin30

## Direct result evidence

For `EP-03_2025_JAN_TOP` beginning 2025-01-01, the committed 504-row result file reports:

E1_TREND_20W:
`indicator_unavailable_days = 0`

E3_CROSS_FAMILY_LADDER:
`indicator_unavailable_days = 0`

for BTC, ETH and ALT_EW.

That is incompatible with a continuity-aware 50/140-day warm-up beginning on 2025-01-01.

The Sep-27 report itself said Jan-2025 was warm-up constrained, so code/results and narrative are inconsistent.

## Consequence

Prior M6 checkpoint language quoting E3:
- median top TWR 1.089;
- minimum top TWR 0.843;
- median drawdown reduction 11.4 pp;
- control median TWR 0.952;

must be read as:

`ORIGINAL_HCEL_OUTPUT_PENDING_TEMPORAL_REVALIDATION`

not as clean reproduced evidence.

The result may survive after repair, weaken, reverse or become less comparable.

UNKNOWN until rerun.

## Separate known defect

E3 partial missingness also has a code/spec mismatch:
`Persist.update(None)` preserves persistence count.

This can:
- keep stale active families active;
- bridge missing periods between otherwise non-consecutive valid observations;
- permit exposure changes while some family state is stale;
- undercount unavailable days.

HCEL O-1 now audits both defects.

## Additional metric caveat

`premature_exit_cost_pct` sums under-exposed positive daily returns.

It is not a compounded terminal wealth difference.

It remains a diagnostic only unless O-1 proves a stronger interpretation.

W_A/W_B/W_C ranking appears to use log terminal-wealth ratio and drawdown reduction rather than this metric, but O-1 must verify.

## Current evidence labels

`HCEL_POLICY_OWNER=YES`

`HCEL_ORIGINAL_RANKING=TEMPORAL_REVALIDATION_REQUIRED`

`E3_PROMOTION=BLOCKED`

`PROSPECTIVE_SHADOW=BLOCKED_PENDING_O1`

`LANE_C_PROTOCOL=FROZEN_COLLECTION_ONLY`

`LIVE_EXIT_RULE=NONE`

## Claude O-1 stop gate

Bridge addendum:
`messages/chatgpt/2026/10/2026-10-05T154100Z_CHATGPT_HCEL_O1_CROSS_WINDOW_STOP_GATE.md`

Required terminal state if material:
`O1_MATERIAL_TEMPORAL_CONTAMINATION_REVIEW_REQUIRED`

No threshold tuning.
No live rule.
No portfolio action.
